"""Receive GCM/FCM messages from google."""

from base64 import b64encode, urlsafe_b64decode, urlsafe_b64encode
from binascii import hexlify
import json
import logging
import os
import os.path
import select
import socket
import ssl
import struct
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import uuid

import appdirs
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from google.protobuf.json_format import MessageToDict
import http_ece
from oscrypto.asymmetric import generate_pair

from .android_checkin_pb2 import AndroidCheckinProto, ChromeBuildProto
from .checkin_pb2 import AndroidCheckinRequest, AndroidCheckinResponse
from .constants import GCF_SENDER_ID
from .mcs_pb2 import (
    Close,
    DataMessageStanza,
    HeartbeatAck,
    HeartbeatPing,
    IqStanza,
    LoginRequest,
    LoginResponse,
    StreamErrorStanza,
)

_LOGGER = logging.getLogger(__name__)

SERVER_KEY = (
    b"\x04\x33\x94\xf7\xdf\xa1\xeb\xb1\xdc\x03\xa2\x5e\x15\x71\xdb\x48\xd3"
    + b"\x2e\xed\xed\xb2\x34\xdb\xb7\x47\x3a\x0c\x8f\xc4\xcc\xe1\x6f\x3c"
    + b"\x8c\x84\xdf\xab\xb6\x66\x3e\xf2\x0c\xd4\x8b\xfe\xe3\xf9\x76\x2f"
    + b"\x14\x1c\x63\x08\x6a\x6f\x2d\xb1\x1a\x95\xb0\xce\x37\xc0\x9c\x6e"
)

REGISTER_URL = "https://android.clients.google.com/c2dm/register3"
CHECKIN_URL = "https://android.clients.google.com/checkin"
FCM_SUBSCRIBE = "https://fcm.googleapis.com/fcm/connect/subscribe"
FCM_ENDPOINT = "https://fcm.googleapis.com/fcm/send"
GOOGLE_MTALK_ENDPOINT = "mtalk.google.com"
READ_TIMEOUT_SECS = 60 * 60
MIN_RESET_INTERVAL_SECS = 60 * 5


def __do_request(req, retries=5):
    for _ in range(retries):
        try:
            resp = urlopen(req)
            resp_data = resp.read()
            resp.close()
            _LOGGER.debug(resp_data)
            return resp_data
        except Exception as err:
            _LOGGER.debug("error during request", exc_info=err)
            time.sleep(1)
    return None


def gcm_check_in(androidId=None, securityToken=None, **kwargs):
    """
    perform check-in request

    androidId, securityToken can be provided if we already did the initial
    check-in

    returns dict with androidId, securityToken and more
    """
    chrome = ChromeBuildProto()
    chrome.platform = 3
    chrome.chrome_version = "63.0.3234.0"
    chrome.channel = 1

    checkin = AndroidCheckinProto()
    checkin.type = 3
    checkin.chrome_build.CopyFrom(chrome)  # pylint: disable=maybe-no-member

    payload = AndroidCheckinRequest()
    payload.user_serial_number = 0
    payload.checkin.CopyFrom(checkin)  # pylint: disable=maybe-no-member
    payload.version = 3
    if androidId:
        payload.id = int(androidId)
    if securityToken:
        payload.security_token = int(securityToken)

    _LOGGER.debug(payload)
    req = Request(
        url=CHECKIN_URL,
        headers={"Content-Type": "application/x-protobuf"},
        data=payload.SerializeToString(),
    )
    resp_data = __do_request(req)
    resp = AndroidCheckinResponse()
    resp.ParseFromString(resp_data)
    _LOGGER.debug(resp)
    return MessageToDict(resp)


def urlsafe_base64(data):
    """
    base64-encodes data with -_ instead of +/ and removes all = padding.
    also strips newlines

    returns a string
    """
    res = urlsafe_b64encode(data).replace(b"=", b"")
    return res.replace(b"\n", b"").decode("ascii")


def gcm_register(appId, retries=5, **kwargs):
    """
    obtains a gcm token

    appId: app id as an integer
    retries: number of failed requests before giving up

    returns {"token": "...", "appId": 123123, "androidId":123123,
             "securityToken": 123123}
    """
    # contains androidId, securityToken and more
    chk = gcm_check_in()
    _LOGGER.debug(chk)
    body = {
        "app": "org.chromium.linux",
        "X-subtype": appId,
        "device": chk["androidId"],
        "sender": urlsafe_base64(SERVER_KEY),
    }
    data = urlencode(body)
    _LOGGER.debug(data)
    auth = "AidLogin {}:{}".format(chk["androidId"], chk["securityToken"])
    req = Request(
        url=REGISTER_URL, headers={"Authorization": auth}, data=data.encode("utf-8")
    )
    for _ in range(retries):
        resp_data = __do_request(req, retries)
        if b"Error" in resp_data:
            err = resp_data.decode("utf-8")
            _LOGGER.error("Register request has failed with %d", err)
            continue
        token = resp_data.decode("utf-8").split("=")[1]
        chkfields = {k: chk[k] for k in ["androidId", "securityToken"]}
        res = {"token": token, "appId": appId}
        res.update(chkfields)
        return res
    return None


def fcm_register(sender_id, token, retries=5):
    """
    generates key pair and obtains a fcm token

    sender_id: sender id as an integer
    token: the subscription token in the dict returned by gcm_register

    returns {"keys": keys, "fcm": {...}}
    """
    # I used this analyzer to figure out how to slice the asn1 structs
    # https://lapo.it/asn1js
    # first byte of public key is skipped for some reason
    # maybe it's always zero
    public, private = generate_pair("ec", curve=str("secp256r1"))

    _LOGGER.debug("# public")
    _LOGGER.debug(b64encode(public.asn1.dump()))
    _LOGGER.debug("# private")
    _LOGGER.debug(b64encode(private.asn1.dump()))
    keys = {
        "public": urlsafe_base64(public.asn1.dump()[26:]),
        "private": urlsafe_base64(private.asn1.dump()),
        "secret": urlsafe_base64(os.urandom(16)),
    }
    data = urlencode(
        {
            "authorized_entity": sender_id,
            "endpoint": "{}/{}".format(FCM_ENDPOINT, token),
            "encryption_key": keys["public"],
            "encryption_auth": keys["secret"],
        }
    )
    _LOGGER.debug(data)
    req = Request(url=FCM_SUBSCRIBE, data=data.encode("utf-8"))
    resp_data = __do_request(req, retries)
    return {"keys": keys, "fcm": json.loads(resp_data.decode("utf-8"))}


def register(sender_id):
    """register gcm and fcm tokens for sender_id"""
    app_id = "wp:receiver.push.com#{}".format(uuid.uuid4())
    subscription = gcm_register(appId=app_id)
    _LOGGER.debug(subscription)
    fcm = fcm_register(sender_id=sender_id, token=subscription["token"])
    _LOGGER.debug(fcm)
    res = {"gcm": subscription}
    res.update(fcm)
    return res


# -------------------------------------------------------------------------


MCS_VERSION = 41

PACKET_BY_TAG = [
    HeartbeatPing,
    HeartbeatAck,
    LoginRequest,
    LoginResponse,
    Close,
    "MessageStanza",
    "PresenceStanza",
    IqStanza,
    DataMessageStanza,
    "BatchPresenceStanza",
    StreamErrorStanza,
    "HttpRequest",
    "HttpResponse",
    "BindAccountRequest",
    "BindAccountResponse",
    "TalkMetadata",
]


def __read(sock, size):
    buf = b""
    while len(buf) < size:
        buf += sock.recv(size - len(buf))
    return buf


# protobuf variable length integers are encoded in base 128
# each byte contains 7 bits of the integer and the msb is set if there's
# more. pretty simple to implement


def __read_varint32(value):
    res = 0
    shift = 0
    while True:
        (b,) = struct.unpack("B", __read(value, 1))
        res |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return res


def __encode_varint32(value):
    res = bytearray([])
    while value != 0:
        b = value & 0x7F
        value >>= 7
        if value != 0:
            b |= 0x80
        res.append(b)
    return bytes(res)


def __send(google_socket, data):
    header = bytearray([MCS_VERSION, PACKET_BY_TAG.index(type(data))])
    _LOGGER.debug(data)
    payload = data.SerializeToString()
    buf = bytes(header) + __encode_varint32(len(payload)) + payload
    _LOGGER.debug(hexlify(buf))
    total = 0
    while total < len(buf):
        sent = google_socket.send(buf[total:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        total += sent


def __recv(data, first=False):

    try:
        readable, _, _ = select.select(
            [
                data,
            ],
            [],
            [],
            READ_TIMEOUT_SECS,
        )
        if len(readable) == 0:
            _LOGGER.debug("Select read timeout")
            return None

    except select.error:
        _LOGGER.debug("Select error")
        return None

    _LOGGER.debug("Data available to read")

    if first:
        version, tag = struct.unpack("BB", __read(data, 2))
        _LOGGER.debug("version %s", version)
        if version < MCS_VERSION and version != 38:
            raise RuntimeError("protocol version {} unsupported".format(version))
    else:
        (tag,) = struct.unpack("B", __read(data, 1))
    _LOGGER.debug("tag %s (%s)", tag, PACKET_BY_TAG[tag])
    size = __read_varint32(data)
    _LOGGER.debug("size %s", size)
    if size >= 0:
        buf = __read(data, size)
        _LOGGER.debug(hexlify(buf))
        packet = PACKET_BY_TAG[tag]
        payload = packet()
        payload.ParseFromString(buf)
        _LOGGER.debug(payload)
        return payload
    return None


def __app_data_by_key(data, key, blow_shit_up=True):
    for item in data.app_data:
        if item.key == key:
            return item.value
    if blow_shit_up:
        raise RuntimeError("couldn't find in app_data {}".format(key))
    return None


def __open():

    context = ssl.create_default_context()
    google_socket = socket.create_connection((GOOGLE_MTALK_ENDPOINT, 5228))
    google_socket = context.wrap_socket(
        google_socket, server_hostname=GOOGLE_MTALK_ENDPOINT
    )
    _LOGGER.debug("connected to ssl socket")
    return google_socket


def __login(credentials, persistent_ids):
    google_socket = __open()

    gcm_check_in(**credentials["gcm"])
    req = LoginRequest()
    req.adaptive_heartbeat = False
    req.auth_service = 2
    req.auth_token = credentials["gcm"]["securityToken"]
    req.id = "chrome-63.0.3234.0"
    req.domain = "mcs.android.com"
    req.device_id = "android-%x" % int(credentials["gcm"]["androidId"])
    req.network_type = 1
    req.resource = credentials["gcm"]["androidId"]
    req.user = credentials["gcm"]["androidId"]
    req.use_rmq2 = True
    req.setting.add(name="new_vc", value="1")  # pylint: disable=maybe-no-member
    req.received_persistent_id.extend(persistent_ids)  # pylint: disable=maybe-no-member
    __send(google_socket, req)
    login_response = __recv(google_socket, first=True)
    _LOGGER.debug("Received login response: %s", login_response)
    return google_socket


def __reset(google_socket, credentials, persistent_ids):
    last_reset = 0
    now = time.time()
    if now - last_reset < MIN_RESET_INTERVAL_SECS:
        raise Exception("Too many connection reset attempts.")
    last_reset = now
    _LOGGER.debug("Reestablishing connection")
    try:
        google_socket.shutdown(2)
        google_socket.close()
    except OSError as err:
        _LOGGER.debug("Unable to close connection %f", err)
    return __login(credentials, persistent_ids)


def __listen(credentials, callback, persistent_ids, obj):
    google_socket = __login(credentials, persistent_ids)

    while True:
        try:
            data = __recv(google_socket)
            if isinstance(data, DataMessageStanza):
                msg_id = __handle_data_message(data, credentials, callback, obj)
                persistent_ids.append(msg_id)
            elif isinstance(data, HeartbeatPing):
                __handle_ping(google_socket, data)
            elif data is None or isinstance(data, Close):
                google_socket = __reset(google_socket, credentials, persistent_ids)
            else:
                _LOGGER.debug("Unexpected message type %s", type(data))
        except ConnectionResetError:
            _LOGGER.debug("Connection Reset: Reconnecting")
            google_socket = __login(credentials, persistent_ids)


def __handle_data_message(data, credentials, callback, obj):
    load_der_private_key = serialization.load_der_private_key

    crypto_key = __app_data_by_key(
        data, "crypto-key", blow_shit_up=False
    )  # Can be None
    if crypto_key:
        crypto_key = crypto_key[3:]  # strip dh=

    salt = __app_data_by_key(data, "encryption", blow_shit_up=False)  # Can be None
    if salt:
        salt = salt[5:]  # strip salt=

    crypto_key = urlsafe_b64decode(crypto_key.encode("ascii"))
    salt = urlsafe_b64decode(salt.encode("ascii"))
    der_data = credentials["keys"]["private"]
    der_data = urlsafe_b64decode(der_data.encode("ascii") + b"========")
    secret = credentials["keys"]["secret"]
    secret = urlsafe_b64decode(secret.encode("ascii") + b"========")
    privkey = load_der_private_key(der_data, password=None, backend=default_backend())
    decrypted = http_ece.decrypt(
        data.raw_data,
        salt=salt,
        private_key=privkey,
        dh=crypto_key,
        version="aesgcm",
        auth_secret=secret,
    )
    _LOGGER.debug("Received data message %s: %s", data.persistent_id, decrypted)
    callback(obj, json.loads(decrypted.decode("utf-8")), data)
    return data.persistent_id


def __handle_ping(google_socket, data):
    _LOGGER.debug(
        "Responding to ping: Stream ID: %s, Last: %s, Status: %s",
        data.stream_id,
        data.last_stream_id_received,
        data.status,
    )
    req = HeartbeatAck()
    req.stream_id = data.stream_id + 1
    req.last_stream_id_received = data.stream_id
    req.status = data.status
    __send(google_socket, req)


def listen(credentials, callback, received_persistent_ids=None, obj=None):
    """
    listens for push notifications

    credentials: credentials object returned by register()
    callback(obj, notification, data_message): called on notifications
    received_persistent_ids: any persistent id's you already received.
                             array of strings
    obj: optional arbitrary value passed to callback
    """

    if received_persistent_ids is None:
        received_persistent_ids = []

    __listen(credentials, callback, received_persistent_ids, obj)


def run_example():
    """sample that registers a token and waits for notifications"""

    logging.basicConfig(level=logging.INFO)

    data_path = appdirs.user_data_dir(appname="push_receiver", appauthor=False)
    try:
        os.makedirs(data_path)
    except FileExistsError:
        pass
    credentials_path = os.path.join(data_path, "credentials.json")
    persistent_ids_path = os.path.join(data_path, "persistent_ids")

    try:
        with open(credentials_path, "r", encoding="UTF-8") as cred_file:
            credentials = json.load(cred_file)

    except FileNotFoundError:
        credentials = register(sender_id=int(GCF_SENDER_ID))
        with open(credentials_path, "w", encoding="UTF-8") as cred_file:
            json.dump(credentials, cred_file)

    _LOGGER.debug(credentials)
    print("send notifications to {}".format(credentials["fcm"]["token"]))

    def on_notification(obj, notification, data_message):
        idstr = data_message.persistent_id + "\n"
        with open(persistent_ids_path, "r", encoding="UTF-8") as cred_file:
            if idstr in cred_file:
                return
        with open(persistent_ids_path, "a", encoding="UTF-8") as cred_file:
            cred_file.write(idstr)
        print("Notification: \n")
        print(json.dumps(notification, indent=2))

    with open(persistent_ids_path, "a+", encoding="UTF-8") as cred_file:
        received_persistent_ids = [x.strip() for x in cred_file]

    listen(credentials, on_notification, received_persistent_ids)

"""Hyyp API constants."""
from enum import Enum

DEFAULT_TIMEOUT = 25
MAX_RETRIES = 3
GCF_SENDER_ID = 87969245803
REQUEST_HEADER = {
    "User-Agent": "okhttp/3.12.1",
}  # Standard android header.
STD_PARAMS = {
    "imei": "152419714130158",  # Alphabet soup starts at 0
    "appVersionCode": "401",
    "_appVersionCode": "401",
    "deviceOS": "12.0",
    "deviceName": "Python API",
    "pkg": "za.co.adt.securehome.android",
    "_appVersionName": "3.5.19",
}  # Standard request parameters.

# Rpc to name mapping. Used in push notifications.
RpcCodes = {
    "202": "IMEI unknown to SMART platform. Registration failed.",
    "203": "Command failed",
    "204": "VALUE is invalid",
    "205": "User code invalid",
    "206": "Unit busy",
    "207": "Command was older than abort command time",
    "208": "Communications timeout to peripheral attached to Hub",
    "209": "Invalid PID in topic",
    "210": "Serial code mismatch",
}

# EventCategory to name mapping.
# Used in notifications.
EventCategory = {"1": "Emergency", "2": "User", "3": "Trouble", "4": "Information"}


class HyypPkg(Enum):
    """Supported hyyp skins/rebranding."""

    ADT_SECURE_HOME = "za.co.adt.securehome.android"
    IDS_HYYP_GENERIC = "com.hyyp247.home"


# EventNumber to name mapping.
EventNumber = {
    "50": "AC clock",
    "13": "AC fail",
    "24": "AC Restore",
    "3": "Alarm cancel",
    "7": "Armed with bypassed zone",
    "43": "Auto arm cancel",
    "0": "Away arm",
    "17": "Battery low",
    "28": "Battery low restore",
    "20": "Box tamper",
    "31": "Box tamper restore",
    "22": "Bus comms fail",
    "33": "Bus comms restore",
    "23": "Bus device battery low",
    "34": "Bus device battery restore",
    "21": "Bus device tamper",
    "32": "Bus device tamper restore",
    "14": "Comms fail",
    "25": "Comm restore",
    "53": "Crossed zone alarm",
    "89": "Cross zone trigger",
    "51": "Crystal oscillator clock",
    "35": "Dedicated panic",
    "2": "Disarm",
    "54": "Disarm from stay",
    "37": "Download access",
    "66": "DTMF login",
    "38": "Duress",
    "18": "12V fuse fail",
    "29": "12V fuse restore",
    "19": "Engineer reset",
    "30": "Engineer reset restore",
    "88": "Entry delay",
    "85": "Exit delay",
    "67": "Failed IDSwift login",
    "90": "Forced door",
    "52": "Installer code changed",
    "45": "Installer mode",
    "40": "Keypad fire",
    "42": "Keypad lockout",
    "41": "Keypad medical",
    "39": "Keypad panic",
    "79": "MPS AC fail",
    "82": "MPS AC restore",
    "80": "MPS batt low",
    "83": "MPS Batt restore",
    "81": "MPS Fuse fail",
    "84": "MPS Fuse restore",
    "48": "Panel defaulted",
    "26": "Phone line restore",
    "15": "Phone line tamper",
    "47": "Power up",
    "92": "Remote arming request",
    "93": "Remote panic",
    "49": "Reserved",
    "72": "RF Detector batt restore",
    "68": "RF Detector low batt",
    "69": "RF Detector supervision loss",
    "73": "RF Detector supervision restore",
    "70": "RF Jam",
    "74": "RF Jam restore",
    "71": "Rf RSSI low",
    "75": "RF RSSI restore",
    "27": "Siren restore",
    "16": "Siren tamper",
    "1": "Stay arm",
    "77": "Stay zone report",
    "230": "System trouble",
    "231": "System trouble restore",
    "91": "TAG arming request",
    "94": "Tamper alarm",
    "100": "User trigger",
    "101": "User panic",
    "36": "Test report",
    "78": "Time stamp",
    "65": "User bypassed zones",
    "46": "User codes defaulted",
    "44": "User code changed",
    "76": "User menu accessed",
    "87": "User unbypassed zones",
    "86": "Voice login lockout",
    "8": "Force armed",
    "6": "Zone restore",
    "11": "Zone shutdown",
    "12": "Zone shutdown restore",
    "9": "Zone tamper",
    "10": "Zone tamper restore",
    "5": "Zone violation alarm",
}

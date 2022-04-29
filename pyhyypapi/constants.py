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


class HyypPkg(Enum):
    """Supported hyyp skins/rebranding."""

    ADT_SECURE_HOME = "za.co.adt.securehome.android"
    IDS_HYYP_GENERIC = "com.hyyp247.home"

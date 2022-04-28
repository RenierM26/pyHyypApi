"""ADT Secure Home API constants."""
from enum import Enum
from random import randint

DEFAULT_TIMEOUT = 25
MAX_RETRIES = 3
REQUEST_HEADER = {
    "User-Agent": "okhttp/3.12.1",
}  # Standard android header.
STD_PARAMS = {
    "imei": "11413"
    + "142114"
    + "11413"
    + "142114"
    + str(randint(0000, 9999)),  # Looks like a random indentifier.
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

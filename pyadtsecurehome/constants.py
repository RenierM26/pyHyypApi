"""ADT Secure Home API constants."""

DEFAULT_TIMEOUT = 25
MAX_RETRIES = 3
REQUEST_HEADER = {
    "User-Agent": "okhttp/3.12.1",
}  # Standard android header.
STD_PARAMS = {
    "imei": "11413142114114131421141111",
    "appVersionCode": "401",
    "_appVersionCode": "401",
    "deviceOS": "12.0",
    "deviceName": "Python API",
    "pkg": "za.co.adt.securehome.android",
    "_appVersionName": "3.5.19",
}  # Standard request parameters.

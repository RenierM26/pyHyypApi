"""Hyyp API constants."""
from enum import Enum, unique

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


@unique
class EventNumber(Enum):
    """EventNumber to name mapping."""

    AC_CLOCK = 50
    AC_FAIL = 13
    AC_RESTORE = 24
    ALARM_CANCEL = 3
    ARMED_WITH_BYPASSED_ZONE = 7
    AUTO_ARM_CANCEL = 43
    AWAY_ARM = 0
    BATTERY_LOW = 17
    BATTERY_LOW_RESTORE = 28
    BOX_TAMPER = 20
    BOX_TAMPER_RESTORE = 31
    BUS_COMMS_FAIL = 22
    BUS_COMMS_RESTORE = 33
    BUS_DEVICE_BATTERY_LOW = 23
    BUS_DEVICE_BATTERY_RESTORE = 34
    BUS_DEVICE_TAMPER = 21
    BUS_DEVICE_TAMPER_RESTORE = 32
    COMMS_FAIL = 14
    COMM_RESTORE = 25
    CROSSED_ZONE_ALARM = 53
    CROSS_ZONE_TRIGGER = 89
    CRYSTAL_OSCILLATOR_CLOCK = 51
    DEDICATED_PANIC = 35
    DISARM = 2
    DISARM_FROM_STAY = 54
    DOWNLOAD_ACCESS = 37
    DTMF_LOGIN = 66
    DURESS = 38
    E12V_FUSE_FAIL = 18
    E12V_FUSE_RESTORE = 29
    ENGINEER_RESET = 19
    ENGINEER_RESET_RESTORE = 30
    ENTRY_DELAY = 88
    EXIT_DELAY = 85
    FAILED_IDSWIFT_LOGIN = 67
    FORCED_DOOR = 90
    INSTALLER_CODE_CHANGED = 52
    INSTALLER_MODE = 45
    KEYPAD_FIRE = 40
    KEYPAD_LOCKOUT = 42
    KEYPAD_MEDICAL = 41
    KEYPAD_PANIC = 39
    MPS_AC_FAIL = 79
    MPS_AC_RESTORE = 82
    MPS_BATT_LOW = 80
    MPS_BATT_RESTORE = 83
    MPS_FUSE_FAIL = 81
    MPS_FUSE_RESTORE = 84
    PANEL_DEFAULTED = 48
    PHONE_LINE_RESTORE = 26
    PHONE_LINE_TAMPER = 15
    POWER_UP = 47
    REMOTE_ARMING_REQUEST = 92
    REMOTE_PANIC = 93
    RESERVED = 49
    RF_DETECTOR_BATT_RESTORE = 72
    RF_DETECTOR_LOW_BATT = 68
    RF_DETECTOR_SUPERVISION_LOSS = 69
    RF_DETECTOR_SUPERVISION_RESTORE = 73
    RF_JAM = 70
    RF_JAM_RESTORE = 74
    RF_RSSI_LOW = 71
    RF_RSSI_RESTORE = 75
    SIREN_RESTORE = 27
    SIREN_TAMPER = 16
    STAY_ARM = 1
    STAY_ZONE_REPORT = 77
    SYSTEM_TROUBLE = 230
    SYSTEM_TROUBLE_RESTORE = 231
    TAG_ARMING_REQUEST = 91
    TAMPER_ALARM = 94
    TEMP_TRIGGER = 100
    TEMP_TRIGGER_ALARM = 101
    TEST_REPORT = 36
    TIME_STAMP = 78
    USER_BYPASSED_ZONES = 65
    USER_CODES_DEFAULTED = 46
    USER_CODE_CHANGED = 44
    USER_MENU_ACCESSED = 76
    USER_UNBYPASSED_ZONES = 87
    VOICE_LOGIN_LOCKOUT = 86
    ZONE_FORCED = 8
    ZONE_RESTORE = 6
    ZONE_SHUTDOWN = 11
    ZONE_SHUTDOWN_RESTORE = 12
    ZONE_TAMPER = 9
    ZONE_TAMPER_RESTORE = 10
    ZONE_VIOLATION_ALARM = 5

"""Hyyp Client API."""
from __future__ import annotations

import logging
from typing import Any

import requests

from .alarm_info import HyypAlarmInfos
from .constants import DEFAULT_TIMEOUT, REQUEST_HEADER, STD_PARAMS, HyypPkg
from .exceptions import HTTPError, HyypApiError, InvalidURL

_LOGGER = logging.getLogger(__name__)

BASE_URL = "ids.trintel.co.za/Inhep-Impl-1.0-SNAPSHOT/"
API_ENDPOINT_LOGIN = "/auth/login"
API_ENDPOINT_CHECK_APP_VERSION = "/auth/checkAppVersion"
API_ENDPOINT_GET_SITE_NOTIFICATIONS = "/device/getSiteNotifications"
API_ENDPOINT_SYNC_INFO = "/device/getSyncInfo"
API_ENDPOINT_STATE_INFO = "/device/getStateInfo"
API_ENDPOINT_NOTIFICATION_SUBSCRIPTIONS = "/device/getNotificationSubscriptions"
API_ENDPOINT_GET_USER_PREFERANCES = "/user/getUserPreferences"
API_ENDPOINT_SET_USER_PREFERANCE = "/user/setUserPreference"
API_ENDPOINT_SECURITY_COMPANIES = "/security-companies/list"
API_ENDPOINT_STORE_GCM_REGISTRATION_ID = "/user/storeGcmRegistrationId"
API_ENDPOINT_ARM_SITE = "/device/armSite"
API_ENDPOINT_TRIGGER_ALARM = "/device/triggerAlarm"
API_ENDPOINT_SET_ZONE_BYPASS = "/device/bypass"
API_ENDPOINT_GET_CAMERA_BY_PARTITION = "/device/getCameraByPartition"
API_ENDPOINT_UPDATE_SUB_USER = "/user/updateSubUser"
API_ENDPOINT_SET_NOTIFICATION_SUBSCRIPTIONS = "/user/setNotificationSubscriptionsNew"


class HyypClient:
    """Initialize api client object."""

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        pkg: str = HyypPkg.ADT_SECURE_HOME.value,
        timeout: int = DEFAULT_TIMEOUT,
        token: str | None = None,
    ) -> None:
        """Initialize the client object."""
        self._email = email
        self._password = password
        self._session = None
        self.close_session()
        STD_PARAMS["pkg"] = pkg
        STD_PARAMS["token"] = token
        self._timeout = timeout

    def login(self) -> dict[Any, Any]:
        """Login to ADT Secure Home API."""

        _params = STD_PARAMS.copy()
        _params["email"] = self._email
        _params["password"] = self._password

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_LOGIN,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(f"Login error: {_json_result['error']}")

        STD_PARAMS["token"] = _json_result["token"]

        return _json_result

    def check_app_version(self) -> dict[Any, Any]:
        """Check App version via API."""

        _params = STD_PARAMS.copy()
        _params["clientImei"] = STD_PARAMS["imei"]

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_CHECK_APP_VERSION,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error checking app version from api: {_json_result['error']}"
            )

        return _json_result

    def load_alarm_infos(self) -> dict[Any, Any]:
        """Get alarm infos formatted for hass infos."""

        return HyypAlarmInfos(self).status()

    def site_notifications(
        self, site_id: int = None, timestamp: int = None, json_key: str = None
    ) -> dict[Any, Any]:
        """Get site notifications from API."""

        if not site_id:
            raise HyypApiError("Please provide site id for this query")

        _params = STD_PARAMS.copy()
        _params["siteId"] = site_id
        _params["timestamp"] = timestamp

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_GET_SITE_NOTIFICATIONS,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting site notifications from api: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result["listSiteNotifications"][site_id]

        return _json_result["listSiteNotifications"][site_id][json_key]

    def set_notification_subscriptions(
        self,
        trouble_notifications: bool = True,
        emergency_notifications: bool = True,
        user_notifications: bool = True,
        information_notifications: bool = True,
        test_report_notifications: bool = False,
    ) -> dict[Any, Any]:
        """Enable or disable app notifications."""

        _params = STD_PARAMS.copy()
        del _params["imei"]
        _params["mobileImei"] = STD_PARAMS["imei"]
        _params["troubleNotifications"] = trouble_notifications
        _params["emergencyNotifications"] = emergency_notifications
        _params["userNotifications"] = user_notifications
        _params["informationNotifications"] = information_notifications
        _params["testReportNotifications"] = test_report_notifications

        try:
            req = self._session.post(
                "https://" + BASE_URL + API_ENDPOINT_SET_NOTIFICATION_SUBSCRIPTIONS,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting site notifications from api: {_json_result['error']}"
            )

        return _json_result

    def get_camera_by_partition(
        self, partition_id: int = None, json_key: str = None
    ) -> dict[Any, Any]:
        """Get cameras, bypassed zones and zone ids by partition from API."""

        if not partition_id:
            raise HyypApiError("Please provide partition id.")

        _params = STD_PARAMS.copy()
        _params["partitionId"] = partition_id

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_GET_CAMERA_BY_PARTITION,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting partition cameras from api: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def get_sync_info(self, json_key: str = None) -> dict[Any, Any]:
        """Get user, site, partition and users info from API."""

        _params = STD_PARAMS

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_SYNC_INFO,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting sync info from api: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def get_state_info(self, json_key: str = None) -> dict[Any, Any]:
        """Get state info from API. Returns armed, bypassed partition ids."""

        _params = STD_PARAMS

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_STATE_INFO,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting state info from api: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def get_notification_subscriptions(self, json_key: str = None) -> dict[Any, Any]:
        """Get notification subscriptions from API."""

        _params = STD_PARAMS

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_NOTIFICATION_SUBSCRIPTIONS,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting notification subscriptions: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def get_user_preferences(
        self, user_id: int = None, site_id: int = None, json_key: str = None
    ) -> dict[Any, Any]:
        """Get user preferences from API."""

        if not user_id:
            raise HyypApiError("A valid user id is required.")

        if not site_id:
            raise HyypApiError("A valid site id is required.")

        _params = STD_PARAMS.copy()
        _params["userId"] = user_id
        _params["siteId"] = site_id

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_GET_USER_PREFERANCES,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Error getting user preferences: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def get_security_companies(self, json_key: str = None) -> dict[Any, Any]:
        """Get security companies from API."""

        _params = STD_PARAMS

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_SECURITY_COMPANIES,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Failed to get security companies: {_json_result['error']}"
            )

        if json_key is None:
            return _json_result

        return _json_result[json_key]

    def store_gcm_registrationid(self, gcm_id: str = None) -> dict[Any, Any]:
        """Store gcmid."""

        _params = STD_PARAMS.copy()
        _params["gcmId"] = gcm_id
        del _params["imei"]
        _params["clientImei"] = STD_PARAMS["imei"]

        try:
            req = self._session.post(
                "https://" + BASE_URL + API_ENDPOINT_STORE_GCM_REGISTRATION_ID,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(f"Storing gcm id failed with: {_json_result['error']}")

        return _json_result

    def set_user_preference(
        self,
        site_id: str = None,
        partition_id: str = None,
        new_code: int = None,
        store_for: str = None,
    ) -> dict[Any, Any]:
        """Set user code preferences."""

        if store_for not in ["Arm", "Bypass"]:
            raise HyypApiError("Invalid selection, choose between Arm or Bypass")

        _params = STD_PARAMS.copy()
        _params["siteId"] = site_id

        _params["name"] = (
            "site." + site_id + ".partition." + partition_id + ".storeFor" + store_for
        )

        _params["preference_value"] = new_code

        try:
            req = self._session.post(
                "https://" + BASE_URL + API_ENDPOINT_SET_USER_PREFERANCE,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Set user preferance failed with: {_json_result['error']}"
            )

        return _json_result

    def set_subuser_preference(
        self,
        site_id: str = None,
        user_id: str = None,
        partition_id: str = None,
        partition_pin: str = None,
        stay_profile_id: int = None,
    ) -> dict[Any, Any]:
        """Set sub user preferences."""

        _params = STD_PARAMS.copy()
        _params["siteId"] = site_id
        _params["userId"] = user_id

        _params["partitions"] = {}
        _params["partitions"][0] = {}
        _params["partitions"][0][".id"] = partition_id
        _params["partitions"][0][".pin"] = partition_pin
        _params["stayProfileIds"] = {}
        _params["stayProfileIds"][0] = stay_profile_id

        try:
            req = self._session.post(
                "https://" + BASE_URL + API_ENDPOINT_UPDATE_SUB_USER,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(
                f"Updating sub user failed with: {_json_result['error']}"
            )

        return _json_result

    def arm_site(
        self,
        arm: bool = True,
        pin: int = None,
        partition_id: int = None,
        site_id: int = None,
        stay_profile_id: int = None,
    ) -> dict[Any, Any]:
        """Arm alarm or stay profile via API."""

        if not site_id:
            raise HyypApiError("Site ID Required")

        _params = STD_PARAMS.copy()
        _params["arm"] = arm
        _params["pin"] = pin
        _params["partitionId"] = partition_id
        _params["siteId"] = site_id
        _params["stayProfileId"] = stay_profile_id
        del _params["imei"]
        _params["clientImei"] = STD_PARAMS["imei"]

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_ARM_SITE,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(f"Arm site failed: {_json_result['error']}")

        return _json_result

    # Untested.
    def trigger_alarm(
        self,
        pin: int = None,
        partition_id: int = None,
        site_id: int = None,
        trigger_id: int = None,
    ) -> dict[Any, Any]:
        """Trigger via API."""

        if not site_id:
            raise HyypApiError("Site ID Required")

        _params = STD_PARAMS.copy()
        _params["pin"] = pin
        _params["partitionId"] = partition_id
        _params["siteId"] = site_id
        _params["triggerId"] = trigger_id
        del _params["imei"]
        _params["clientImei"] = STD_PARAMS["imei"]

        try:
            req = self._session.post(
                "https://" + BASE_URL + API_ENDPOINT_TRIGGER_ALARM,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(f"Trigger alarm failed: {_json_result['error']}")

        return _json_result

    def set_zone_bypass(
        self,
        partition_id: int = None,
        zones: int = None,
        stay_profile_id: int = 0,
        pin: int = None,
    ) -> dict[Any, Any]:
        """Set/toggle zone bypass."""

        if not zones:
            raise HyypApiError("Requires zone id")

        _params = STD_PARAMS.copy()
        _params["partitionId"] = partition_id
        _params["zones"] = zones
        _params["stayProfileId"] = stay_profile_id
        _params["pin"] = pin
        del _params["imei"]
        _params["clientImei"] = STD_PARAMS["imei"]

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_SET_ZONE_BYPASS,
                allow_redirects=False,
                params=_params,
                timeout=self._timeout,
            )

            req.raise_for_status()

        except requests.ConnectionError as err:
            raise InvalidURL("A Invalid URL or Proxy error occured") from err

        except requests.HTTPError as err:
            raise HTTPError from err

        try:
            _json_result = req.json()

        except ValueError as err:
            raise HyypApiError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS" and _json_result["error"] is not None:
            raise HyypApiError(f"Failed to set zone bypass: {_json_result['error']}")

        return _json_result

    def logout(self) -> None:
        """Close ADT Secure Home session."""
        self.close_session()

    def close_session(self) -> None:
        """Clear current session."""
        if self._session:
            self._session.close()

        self._session = requests.session()
        self._session.headers.update(REQUEST_HEADER)  # Reset session.

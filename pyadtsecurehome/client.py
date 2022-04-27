"""ADT Secure Home API."""
from __future__ import annotations

import logging
from typing import Any
from .exceptions import PyAdtSecureHomeError, InvalidURL, HTTPError
from .constants import DEFAULT_TIMEOUT, REQUEST_HEADER, STD_PARAMS

import requests

_LOGGER = logging.getLogger(__name__)

BASE_URL = "ids.trintel.co.za/Inhep-Impl-1.0-SNAPSHOT/"
API_ENDPOINT_LOGIN = "/auth/login"
API_ENDPOINT_SITE_NOTIFICATIONS = "/device/getSiteNotifications"


class PyAdtSecureHome:
    """Initialize api client object."""

    def __init__(
        self,
        email: str | None = None,
        password: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        token: str | None = None,
    ) -> None:
        """Initialize the client object."""
        self._email = email
        self._password = password
        self._session = None
        self.close_session()
        self._token = token
        self._timeout = timeout

    def login(self) -> dict[Any, Any]:
        """Login to ADT Secure Home API."""

        _params = STD_PARAMS
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
            raise PyAdtSecureHomeError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS":
            raise PyAdtSecureHomeError(f"Login error: {_json_result['meta']}")

        self._token = _json_result["token"]

        return _json_result

    def site_notifications(self) -> dict[Any, Any]:
        """Get site notifications from API."""

        _params = STD_PARAMS
        _params["token"] = self._token

        try:
            req = self._session.get(
                "https://" + BASE_URL + API_ENDPOINT_SITE_NOTIFICATIONS,
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
            raise PyAdtSecureHomeError(
                "Impossible to decode response: "
                + str(err)
                + "\nResponse was: "
                + str(req.text)
            ) from err

        if _json_result["status"] != "SUCCESS":
            raise PyAdtSecureHomeError(f"Login error: {_json_result['meta']}")

        self._token = _json_result["token"]

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

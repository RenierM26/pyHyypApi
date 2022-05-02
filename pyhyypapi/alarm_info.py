"""Alarm info for hass integration."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .constants import EventNumber

if TYPE_CHECKING:
    from .client import HyypClient


class HyypAlarmInfos:
    """Initialize Hyyp alarm objects."""

    def __init__(self, client: HyypClient) -> None:
        """init."""
        self._client = client
        self._sync_info: dict = {}
        self._state_info: dict = {}

    def _fetch_data(self) -> None:
        """Fetch data via client api."""
        self._sync_info = self._client.get_sync_info()
        self._state_info = self._client.get_state_info()

    def _last_notice(self, site_id: str) -> dict[Any, Any]:
        """Get last notification."""
        _response = {"dateTime": None, "eventName": None}

        _last_notification = self._client.site_notifications(
            site_id=site_id, json_key=0
        )

        _last_event = _last_notification["eventNumber"]
        _last_event_datetime = _last_notification["dateTime"]

        _response = {
            "dateTime": _last_event_datetime,
            "eventName": EventNumber[str(_last_event)],
        }

        return _response

    def _format_data(self) -> dict[Any, Any]:
        """Format data for Hass."""

        # The API returns data from site level, need to invert.
        # Partitions are used as actual entity that actions are performed on.

        site_ids = {site["id"]: site for site in self._sync_info["sites"]}
        zone_ids = {zone["id"]: zone for zone in self._sync_info["zones"]}
        stay_ids = {
            stay_profile["id"]: stay_profile
            for stay_profile in self._sync_info["stayProfiles"]
        }
        partition_ids = {
            partition["id"]: partition for partition in self._sync_info["partitions"]
        }

        for partition in partition_ids:

            # Add site info.
            partition_ids[partition]["site"] = {
                key: value
                for (key, value) in site_ids.items()
                if partition in value["partitionIds"]
            }

            # Add zone info.
            partition_ids[partition]["zones"] = {
                key: value
                for (key, value) in zone_ids.items()
                if key in partition_ids[partition]["zoneIds"]
            }

            # Add stay profile info.
            partition_ids[partition]["stayProfile"] = {
                key: value
                for (key, value) in stay_ids.items()
                if key in partition_ids[partition]["stayProfileIds"]
            }

            # Add zone bypass info.
            for zone in partition_ids[partition]["zones"]:
                if zone in self._state_info["bypassedZoneIds"]:
                    partition_ids[partition]["zones"][zone]["bypassed"] = True
                else:
                    partition_ids[partition]["zones"][zone]["bypassed"] = False

            # Add partition armed status.
            if partition in self._state_info["armedPartitionIds"]:
                partition_ids[partition]["armed"] = True

            else:
                partition_ids[partition]["armed"] = False

            # Add partition stay_armed status.
            for stay_profile in partition_ids[partition]["stayProfile"]:
                if stay_profile in self._state_info["armedStayProfileIds"]:
                    partition_ids[partition]["stayArmed"] = partition_ids[partition][
                        "stayProfile"
                    ][stay_profile]["name"]

                else:
                    partition_ids[partition]["stayArmed"] = False

            # Add last site notification.
            partition_ids[partition]["lastNotification"] = self._last_notice(
                site_id=str(list(partition_ids[partition]["site"])[0])
            )

        return partition_ids

    def status(self) -> dict[Any, Any]:
        """Return the status of Hyyp connected alarms."""

        self._fetch_data()
        formatted_data: dict[Any, Any] = self._format_data()

        return formatted_data

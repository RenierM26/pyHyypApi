"""Alarm info for hass integration."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from datetime import datetime
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

    def _last_notice(self, site_id: int) -> dict[Any, Any]:
        """Get last notification."""
        _response: dict[Any, Any] = {"lastNoticeTime": None, "lastNoticeName": None}

        _last_notification = self._client.site_notifications(
            site_id=site_id, json_key=0
        )

        _last_event = _last_notification["eventNumber"]
        _last_event_datetime = str(
            datetime.fromtimestamp(_last_notification["timestamp"] / 1000)
        )  # Epoch in ms

        _response = {
            "lastNoticeTime": _last_event_datetime,
            "lastNoticeName": EventNumber[str(_last_event)],
        }

        return _response

    def _format_data(self) -> dict[Any, Any]:
        """Format data for Hass."""

        # The API returns data from site level.
        # Partitions are used as entity that actions are performed on.

        site_ids = {site["id"]: site for site in self._sync_info["sites"]}
        zone_ids = {zone["id"]: zone for zone in self._sync_info["zones"]}
        stay_ids = {
            stay_profile["id"]: stay_profile
            for stay_profile in self._sync_info["stayProfiles"]
        }
        partition_ids = {
            partition["id"]: partition for partition in self._sync_info["partitions"]
        }

        for site in site_ids:

            # Add last site notification.
            _last_notice = self._last_notice(site_id=site)
            site_ids[site]["lastNoticeTime"] = _last_notice["lastNoticeTime"]
            site_ids[site]["lastNoticeName"] = _last_notice["lastNoticeName"]

            # Add partition info.
            site_ids[site]["partitions"] = {
                partition_id: partition_ids[partition_id]
                for partition_id in site_ids[site]["partitionIds"]
            }

            for partition in partition_ids:
                # Add zone info to partition.
                site_ids[site]["partitions"][partition]["zones"] = {
                    key: value
                    for (key, value) in zone_ids.items()
                    if key in site_ids[site]["partitions"][partition]["zoneIds"]
                }

                # Add zone bypass info to zone.
                for zone in site_ids[site]["partitions"][partition]["zones"]:
                    site_ids[site]["partitions"][partition]["zones"][zone][
                        "bypassed"
                    ] = bool(zone in self._state_info["bypassedZoneIds"])

                # Add stay profile info.
                site_ids[site]["partitions"][partition]["stayProfiles"] = {
                    key: value
                    for (key, value) in stay_ids.items()
                    if key in site_ids[site]["partitions"][partition]["stayProfileIds"]
                }

                # Add partition armed status.
                site_ids[site]["partitions"][partition]["armed"] = bool(
                    partition in self._state_info["armedPartitionIds"]
                )

                # Add partition stay_armed status.
                for stay_profile in site_ids[site]["partitions"][partition][
                    "stayProfiles"
                ]:
                    site_ids[site]["partitions"][partition]["stayArmed"] = bool(
                        stay_profile in self._state_info["armedStayProfileIds"]
                    )
                    site_ids[site]["partitions"][partition]["stayArmedProfileName"] = (
                        site_ids[site]["partitions"][partition]["stayProfiles"][
                            stay_profile
                        ]["name"]
                        if stay_profile in self._state_info["armedStayProfileIds"]
                        else None
                    )

        return site_ids

    def status(self) -> dict[Any, Any]:
        """Return the status of Hyyp connected alarms."""

        self._fetch_data()
        formatted_data: dict[Any, Any] = self._format_data()

        return formatted_data

"""Useful things for dealing with time."""

import zoneinfo

import whenever


class TimeSource:
    """An interface for getting the current time."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__time_zone_name = ""

    def get_time_zone_name(self) -> str:
        """Get the name of the time zone."""
        return self.__time_zone_name

    def set_time_zone_name(self, time_zone_name: str) -> None:
        """Set the name of the time zone."""
        try:
            _zone_info = zoneinfo.ZoneInfo(time_zone_name)

        except Exception as exception:
            raise ValueError("Invalid time zone name.") from exception

        self.__time_zone_name = time_zone_name

    def get_current_time(self) -> whenever.ZonedDateTime:
        """Get the current time in the current time zone."""
        time_zone_name = self.get_time_zone_name()
        global_time = whenever.Instant.now()
        return global_time.to_tz(time_zone_name)

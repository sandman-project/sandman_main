"""Useful things for dealing with time."""

import tzlocal
import whenever


class TimeSource:
    """An interface for getting the current time."""

    def __init__(self) -> None:
        """Initialize the instance."""
        pass

    def get_current_time_zone_name(self) -> str:
        """Get the name of the current time zone."""
        return tzlocal.get_localzone_name()

    def get_current_time(self) -> whenever.ZonedDateTime:
        """Get the current time in the current time zone."""
        time_zone_name = self.get_current_time_zone_name()
        global_time = whenever.Instant.now()
        return global_time.to_tz(time_zone_name)

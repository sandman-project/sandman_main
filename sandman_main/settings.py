"""Provides support for overall settings, not specific to a system."""

import logging
import pathlib
import zoneinfo

_logger = logging.getLogger("sandman.settings")


class Settings:
    """Specifies the overall settings."""

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__time_zone_name: str = ""

    @property
    def time_zone_name(self) -> str:
        """Get the time zone name."""
        return self.__time_zone_name

    @time_zone_name.setter
    def time_zone_name(self, time_zone_name: str) -> None:
        """Set the time zone name."""
        if isinstance(time_zone_name, str) == False:
            raise TypeError("Time zone name must be a string.")

        try:
            _zone_info = zoneinfo.ZoneInfo(time_zone_name)

        except Exception as exception:
            raise ValueError("Invalid time zone name.") from exception

        self.__time_zone_name = time_zone_name


def bootstrap_settings(base_dir: str) -> None:
    """Handle bootstrapping for settings."""
    settings_path = pathlib.Path(base_dir + "settings.cfg")

    if settings_path.exists() == True:
        return

    _logger.info("Creating missing settings file '%s'.", str(settings_path))

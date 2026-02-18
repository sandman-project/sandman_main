"""Provides support for overall settings, not specific to a system."""

import json
import logging
import pathlib
import typing
import zoneinfo

_logger = logging.getLogger("sandman.settings")


class Settings:
    """Specifies the overall settings."""

    DEFAULT_TIME_ZONE_NAME = "America/Chicago"
    DEFAULT_STARTUP_DELAY_SEC = 4

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__time_zone_name: str = self.DEFAULT_TIME_ZONE_NAME
        self.__startup_delay_sec: int = self.DEFAULT_STARTUP_DELAY_SEC

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

    @property
    def startup_delay_sec(self) -> int:
        """Get the startup delay (in seconds)."""
        return self.__startup_delay_sec

    @startup_delay_sec.setter
    def startup_delay_sec(self, startup_delay_sec: int) -> None:
        """Set the startup delay (in seconds)."""
        if isinstance(startup_delay_sec, int) == False:
            raise TypeError("Startup delay must be an integer.")

        if startup_delay_sec < 0:
            raise ValueError("Startup delay must be non-negative.")

        self.__startup_delay_sec = startup_delay_sec

    def is_valid(self) -> bool:
        """Check whether these are valid settings."""
        try:
            _zone_info = zoneinfo.ZoneInfo(self.__time_zone_name)

        except Exception:
            return False

        if self.__startup_delay_sec < 0:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether these settings and another have equal values."""
        if not isinstance(other, Settings):
            return NotImplemented

        return (self.__time_zone_name == other.__time_zone_name) and (
            self.__startup_delay_sec == other.__startup_delay_sec
        )

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse settings from a file."""
        new_settings = cls()

        try:
            with open(filename) as file:
                try:
                    settings_json = json.load(file)

                except json.JSONDecodeError:
                    _logger.error(
                        "JSON error decoding settings file '%s'.",
                        filename,
                    )
                    return new_settings

                try:
                    new_settings.time_zone_name = settings_json["timeZoneName"]

                except KeyError:
                    _logger.warning(
                        "Missing 'timeZoneName' key in settings file '%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid time zone name '%s' in settings file '%s'.",
                        str(settings_json["timeZoneName"]),
                        filename,
                    )

                try:
                    new_settings.startup_delay_sec = settings_json[
                        "startupDelaySec"
                    ]

                except KeyError:
                    _logger.warning(
                        "Missing 'startupDelaySec' key in settings file '%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid startup delay '%s' in settings file '%s'.",
                        str(settings_json["startupDelaySec"]),
                        filename,
                    )

        except FileNotFoundError as error:
            _logger.error("Could not find settings file '%s'.", filename)
            raise error

        return new_settings

    def save_to_file(self, filename: str) -> None:
        """Save settings to a file."""
        if self.is_valid() == False:
            _logger.warning("Cannot save invalid settings to '%s'", filename)
            return

        settings_json = {
            "timeZoneName": self.__time_zone_name,
            "startupDelaySec": self.__startup_delay_sec,
        }

        try:
            with open(filename, "w") as file:
                json.dump(settings_json, file, indent=4)

        except OSError as error:
            _logger.error("Failed to open '%s' to save settings.", filename)
            raise error


def bootstrap_settings(base_dir: str) -> None:
    """Handle bootstrapping for settings."""
    settings_path = pathlib.Path(base_dir + "settings.cfg")

    if settings_path.exists() == True:
        return

    _logger.info("Creating missing settings file '%s'.", str(settings_path))

    # Set up some default settings.
    new_settings = Settings()

    new_settings.save_to_file(str(settings_path))


def load_or_create_settings(base_dir: str) -> Settings:
    """Load or create settings.

    If settings are missing, default values are saved. If they exist but have
    any missing or invalid values, they will be replaced by defaults and
    saved.
    """
    settings_path = pathlib.Path(base_dir + "settings.cfg")

    if settings_path.exists() == False:
        _logger.info(
            "Creating missing settings file '%s'.", str(settings_path)
        )

        new_settings = Settings()
        new_settings.save_to_file(str(settings_path))

        return new_settings

    loaded_settings = Settings.parse_from_file(str(settings_path))
    loaded_settings.save_to_file(str(settings_path))

    return loaded_settings

"""Provides support for overall settings, not specific to a system."""

import json
import logging
import pathlib
import typing
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

    def is_valid(self) -> bool:
        """Check whether these are valid settings."""
        try:
            _zone_info = zoneinfo.ZoneInfo(self.__time_zone_name)

        except Exception:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether these settings and another have equal values."""
        if not isinstance(other, Settings):
            return NotImplemented

        return self.__time_zone_name == other.__time_zone_name

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

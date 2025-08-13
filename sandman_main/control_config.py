"""Provides configuration for controls."""

import json
import logging
import pathlib
import typing

_logger = logging.getLogger("sandman.control_config")


class ControlConfig:
    """Specifies the configuration of a control."""

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__name: str = ""
        self.__up_gpio_line: int = -1
        self.__down_gpio_line: int = -1
        self.__moving_duration_ms: int = -1
        self.__cool_down_duration_ms: int = 25

    @property
    def name(self) -> str:
        """Get the name."""
        return self.__name

    @name.setter
    def name(self, new_name: str) -> None:
        """Set the name."""
        if isinstance(new_name, str) == False:
            raise TypeError("Name must be a string.")

        if new_name == "":
            raise ValueError("Cannot set an empty name.")

        self.__name = new_name

    @property
    def up_gpio_line(self) -> int:
        """Get the up GPIO line."""
        return self.__up_gpio_line

    @up_gpio_line.setter
    def up_gpio_line(self, line: int) -> None:
        """Set the up GPIO line."""
        if isinstance(line, int) == False:
            raise TypeError("GPIO line must be an integer.")

        if line < 0:
            raise ValueError("GPIO line cannot be negative.")

        self.__up_gpio_line = line

    @property
    def down_gpio_line(self) -> int:
        """Get the down GPIO line."""
        return self.__down_gpio_line

    @down_gpio_line.setter
    def down_gpio_line(self, line: int) -> None:
        """Set the down GPIO line."""
        if isinstance(line, int) == False:
            raise TypeError("GPIO line must be an integer.")

        if line < 0:
            raise ValueError("GPIO line cannot be negative.")

        self.__down_gpio_line = line

    @property
    def moving_duration_ms(self) -> int:
        """Get the moving duration."""
        return self.__moving_duration_ms

    @moving_duration_ms.setter
    def moving_duration_ms(self, duration_ms: int) -> None:
        """Set the moving duration."""
        if isinstance(duration_ms, int) == False:
            raise TypeError("Duration must be an integer.")

        if duration_ms < 0:
            raise ValueError("Duration cannot be negative.")

        self.__moving_duration_ms = duration_ms

    @property
    def cool_down_duration_ms(self) -> int:
        """Get the cool down duration."""
        return self.__cool_down_duration_ms

    @cool_down_duration_ms.setter
    def cool_down_duration_ms(self, duration_ms: int) -> None:
        """Set the cool down duration."""
        if isinstance(duration_ms, int) == False:
            raise TypeError("Duration must be an integer.")

        if duration_ms < 0:
            raise ValueError("Duration cannot be negative.")

        self.__cool_down_duration_ms = duration_ms

    def is_valid(self) -> bool:
        """Check whether this is a valid control config."""
        if self.__name == "":
            return False

        if self.__up_gpio_line < 0:
            return False

        if self.__down_gpio_line < 0:
            return False

        # GPIO lines cannot be the same.
        if self.__up_gpio_line == self.__down_gpio_line:
            return False

        if self.__moving_duration_ms < 0:
            return False

        if self.__cool_down_duration_ms < 0:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this config and another have equal values."""
        if not isinstance(other, ControlConfig):
            return NotImplemented

        return (
            (self.__name == other.__name)
            and (self.__up_gpio_line == other.__up_gpio_line)
            and (self.__down_gpio_line == other.__down_gpio_line)
            and (self.__moving_duration_ms == other.__moving_duration_ms)
            and (self.__cool_down_duration_ms == other.__cool_down_duration_ms)
        )

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse a config from a file."""
        config = cls()

        try:
            with open(filename) as file:
                try:
                    config_json = json.load(file)

                except json.JSONDecodeError:
                    _logger.error(
                        "JSON error decoding control config file '%s'.",
                        filename,
                    )
                    return config

                try:
                    config.name = config_json["name"]

                except KeyError:
                    _logger.warning(
                        "Missing 'name' key in control config file '%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid name '%s' in control config file '%s'.",
                        str(config_json["name"]),
                        filename,
                    )

                try:
                    config.up_gpio_line = config_json["upGPIOLine"]

                except KeyError:
                    _logger.warning(
                        "Missing 'up GPIO line' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid up GPIO line '%s' in control config file "
                        + "'%s'.",
                        str(config_json["upGPIOLine"]),
                        filename,
                    )

                try:
                    config.down_gpio_line = config_json["downGPIOLine"]

                except KeyError:
                    _logger.warning(
                        "Missing 'down GPIO line' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid down GPIO line '%s' in control config file "
                        + "'%s'.",
                        str(config_json["downGPIOLine"]),
                        filename,
                    )

                try:
                    config.moving_duration_ms = config_json["movingDurationMS"]

                except KeyError:
                    _logger.warning(
                        "Missing 'moving duration' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid moving duration '%s' in control config file "
                        + "'%s'.",
                        str(config_json["movingDurationMS"]),
                        filename,
                    )

                try:
                    config.cool_down_duration_ms = config_json[
                        "coolDownDurationMS"
                    ]

                except KeyError:
                    # This is acceptable.
                    pass

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid cool down duration '%s' in control config "
                        + "file '%s'.",
                        str(config_json["coolDownDurationMS"]),
                        filename,
                    )

        except FileNotFoundError as error:
            _logger.error("Could not find control config file '%s'.", filename)
            raise error

        return config

    def save_to_file(self, filename: str) -> None:
        """Save a config to a file."""
        if self.is_valid() == False:
            _logger.warning(
                "Cannot save invalid control config to '%s'", filename
            )
            return

        config_json = {
            "name": self.__name,
            "upGPIOLine": self.__up_gpio_line,
            "downGPIOLine": self.__down_gpio_line,
            "movingDurationMS": self.__moving_duration_ms,
            "coolDownDurationMS": self.__cool_down_duration_ms,
        }

        try:
            with open(filename, "w") as file:
                json.dump(config_json, file)

        except OSError as error:
            _logger.error(
                "Failed to open '%s' to save control config.", filename
            )
            raise error


def bootstrap_control_configs(base_dir: str) -> None:
    """Handle bootstrapping for control configs."""
    control_path = pathlib.Path(base_dir + "controls/")

    if control_path.exists() == True:
        return

    _logger.info(
        "Creating missing control config directory '%s'.", str(control_path)
    )

    try:
        control_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create control config directory '%s'.",
            str(control_path),
        )
        return

    # Now that the directory exists, populate it with some default controls.

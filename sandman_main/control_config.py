"""Provides configuration for controls."""

import json
import typing


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

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse a config from a file."""
        config = cls()

        try:
            with open(filename) as file:
                try:
                    config_json = json.load(file)

                except json.JSONDecodeError:
                    # Log this.
                    return config

                config.name = config_json["name"]

        except FileNotFoundError as error:
            # Log this.
            raise error

        return config

"""Provides configuration for controls."""


class ControlConfig:
    """Specifies the configuration of a control."""

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__name: str = ""
        self.__up_gpio_line = -1
        self.__down_gpio_line = -1

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

        return True

"""Manages GPIO, which is used by the controls to move the bed."""

import logging

import gpiod


class GPIOManager:
    """Manages access to GPIO functionality."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__logger: logging.Logger = logging.getLogger(
            "sandman.gpio_manager"
        )
        self.__chip: gpiod.Chip | None = None

    def initialize(self) -> None:
        """Set up the manager for use."""
        chip_path: str = "/dev/gpiochip0"

        try:
            self.__chip = gpiod.Chip(chip_path)

        except OSError:
            self.__logger.warning("Failed to open GPIO chip %s", chip_path)
            return

    def uninitialize(self) -> None:
        """Clean up the manager after use."""
        if self.__chip is not None:
            self.__chip.close()
            self.__chip = None

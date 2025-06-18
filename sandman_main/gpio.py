"""Manages GPIO, which is used by the controls to move the bed.

NOTE - Acquires exclusive access to GPIO lines.
"""

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
        self.__line_requests: dict[int, gpiod.line_request.LineRequest] = {}

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

    @property
    def acquired_lines(self) -> list[int]:
        """Access a list of the acquired lines."""
        return list(self.__line_requests)

    def acquire_output_line(self, line: int) -> bool:
        """Acquire a line for output."""
        if self.__chip is None:
            return False

        return False

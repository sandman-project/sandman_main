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
        for line in self.acquired_lines:
            self.release_output_line(line)

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
            self.__logger.warning(
                "Tried to acquire output line %d, but there is no chip.", line
            )
            return False

        if line in self.__line_requests:
            self.__logger.info(
                "Ignoring request to acquire output line %d because it has "
                + "already been acquired.",
                line,
            )
            return False

        try:
            request: gpiod.LineRequest = self.__chip.request_lines(
                consumer="sandman",
                config={
                    line: gpiod.LineSettings(
                        direction=gpiod.line.Direction.OUTPUT,
                        output_value=gpiod.line.Value.ACTIVE,
                    )
                },
            )

        except ValueError:
            self.__logger.warning("Failed to acquire output line %d.", line)
            return False

        if request == False:
            self.__logger.warning("Failed to acquire output line %d.", line)
            return False

        self.__line_requests[line] = request
        return True

    def release_output_line(self, line: int) -> bool:
        """Release a line that was acquired output."""
        if line not in self.__line_requests:
            self.__logger.info(
                "Tried to release output line %d, but was not acquired.", line
            )
            return False

        self.__line_requests[line].release()
        del self.__line_requests[line]

        if self.__chip is None:
            return True

        # Set the line back to input.
        request: gpiod.LineRequest = self.__chip.request_lines(
            consumer="sandman",
            config={
                line: gpiod.LineSettings(
                    direction=gpiod.line.Direction.INPUT,
                    output_value=gpiod.line.Value.ACTIVE,
                )
            },
        )
        request.release()

        return True

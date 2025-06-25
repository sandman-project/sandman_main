"""Manages GPIO, which is used by the controls to move the bed.

NOTE - Acquires exclusive access to GPIO lines.
"""

import logging

import gpiod


class GPIOManager:
    """Manages access to GPIO functionality."""

    def __init__(self, is_live_mode: bool) -> None:
        """Initialize the instance.

        is_live_mode - If this is True, then actions will affect the actual
            GPIO chip, otherwise they will not (which is appropriate for
            running tests off device).
        """
        self.__logger: logging.Logger = logging.getLogger(
            "sandman.gpio_manager"
        )
        self.__chip: gpiod.Chip | None = None
        self.__line_requests: dict[
            int, gpiod.line_request.LineRequest | None
        ] = {}
        self.__is_live_mode: bool = is_live_mode
        self.__initialized: bool = False

    def initialize(self) -> None:
        """Set up the manager for use."""
        if self.__is_live_mode == False:
            self.__initialized = True
            return

        chip_path: str = "/dev/gpiochip0"

        try:
            self.__chip = gpiod.Chip(chip_path)

        except OSError:
            self.__logger.warning("Failed to open GPIO chip %s", chip_path)
            return

        self.__initialized = True

    def uninitialize(self) -> None:
        """Clean up the manager after use."""
        for line in self.acquired_lines:
            self.release_output_line(line)

        if self.__chip is not None:
            self.__chip.close()
            self.__chip = None

        self.__initialized = False

    @property
    def acquired_lines(self) -> list[int]:
        """Access a list of the acquired lines."""
        return list(self.__line_requests)

    def acquire_output_line(self, line: int) -> bool:
        """Acquire a line for output."""
        if self.__initialized == False:
            return False

        if (self.__chip is None) and (self.__is_live_mode == True):
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

        # When not in live mode, pretend that the line was requested.
        if self.__is_live_mode == False:
            self.__line_requests[line] = None
            return True

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
                "Tried to release output line %d, but it is not acquired.",
                line,
            )
            return False

        # Only release the line in live mode (it will be None otherwise).
        if self.__is_live_mode == True:
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

    def set_line_active(self, line: int) -> bool:
        """Set the line to active (high)."""
        # For some reason our values need to be inverted. This may be an issue
        # with the hardware set up.
        return self.__set_line_value(line, gpiod.line.Value.INACTIVE)

    def set_line_inactive(self, line: int) -> bool:
        """Set the line to inactive (low)."""
        # For some reason our values need to be inverted. This may be an issue
        # with the hardware set up.
        return self.__set_line_value(line, gpiod.line.Value.ACTIVE)

    def __set_line_value(self, line: int, value: gpiod.line.Value) -> bool:
        """Set the value of an output line."""
        if line not in self.__line_requests:
            self.__logger.info(
                "Tried to set output line %d value, but it is not acquired.",
                line,
            )
            return False

        # Only set the value in live mode (it will be None otherwise).
        if self.__is_live_mode == True:
            self.__line_requests[line].set_value(line, value)

        return True

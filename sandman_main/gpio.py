"""Manages GPIO, which is used by the controls to move the bed."""

import logging

import gpiod


class GPIOManager:
    """Manages access to GPIO functionality."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.gpio_manager")
        self.__chip = None

        chip_path = "/dev/gpiochip0"

        try:
            self.__chip = gpiod.Chip(chip_path)

        except OSError:
            self.__logger.warning("Failed to open GPIO chip %s", chip_path)

        if self.__chip is None:
            return

        with self.__chip.request_lines(
            consumer="sandman-test",
            config={
                20: gpiod.LineSettings(
                    direction=gpiod.line.Direction.OUTPUT,
                    output_value=gpiod.line.Value.ACTIVE,
                )
            },
        ) as request:
            request.set_value(20, gpiod.line.Value.ACTIVE)

        # Cleanup on destruction?
        self.__chip.close()

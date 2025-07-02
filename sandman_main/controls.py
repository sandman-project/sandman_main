"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import enum
import logging

import gpio
import timer


@enum.unique
class ControlState(enum.Enum):
    """The various states a control can be in."""

    IDLE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    COOL_DOWN = 3


_state_names = [
    "idle",  # IDLE
    "move up",  # MOVE_UP
    "move down",  # MOVE_DOWN
    "cool down",  # COOL_DOWN
]


class Control:
    """The state and logic for a control that manages a part of the bed."""

    def __init__(
        self,
        name: str,
        timer: timer.Timer,
        gpio_manager: gpio.GPIOManager,
    ) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = ControlState.IDLE
        self.__desired_state = ControlState.IDLE
        self.__name = name
        self.__timer = timer
        self.__gpio_manager: gpio.GPIOManager = gpio_manager
        self.__up_gpio_line: int = -1
        self.__down_gpio_line: int = -1
        self.__moving_duration_ms: int = -1
        self.__cool_down_duration_ms: int = -1
        self.__initialized = False

    def initialize(
        self,
        up_gpio_line: int,
        down_gpio_line: int,
        moving_duration_ms: int,
        cool_down_duration_ms: int,
    ) -> bool:
        """Initialize the control for use."""
        if self.__initialized == True:
            self.__logger.error(
                "Tried to initialize control, but it's already initialized."
            )
            return False

        if up_gpio_line < 0:
            self.__logger.error(
                "Invalid GPIO line for moving up: %d.", up_gpio_line
            )
            return False

        if down_gpio_line < 0:
            self.__logger.error(
                "Invalid GPIO line for moving down: %d.", down_gpio_line
            )
            return False

        if up_gpio_line == down_gpio_line:
            self.__logger.error(
                "Control must use different GPIO lines for moving up and down."
            )
            return False

        if moving_duration_ms < 1:
            self.__logger.error(
                "Invalid moving duration for control: %d ms.",
                moving_duration_ms,
            )
            return False

        if cool_down_duration_ms < 0:
            self.__logger.error(
                "Invalid cool down duration for control: %d ms.",
                cool_down_duration_ms,
            )
            return False

        self.__up_gpio_line = up_gpio_line
        self.__down_gpio_line = down_gpio_line
        self.__moving_duration_ms = moving_duration_ms
        self.__cool_down_duration_ms = cool_down_duration_ms

        # Try to acquire the GPIO lines.
        if (
            self.__gpio_manager.acquire_output_line(self.__up_gpio_line)
            == False
        ):
            self.__logger.error("Failed to acquire up GPIO line.")
            return False

        if (
            self.__gpio_manager.acquire_output_line(self.__down_gpio_line)
            == False
        ):
            self.__logger.error("Failed to acquire down GPIO line.")
            self.__gpio_manager.release_output_line(self.__up_gpio_line)
            return False

        # This should be redundant, but set both lines to an active just in
        # case.
        self.__gpio_manager.set_line_inactive(self.__up_gpio_line)
        self.__gpio_manager.set_line_inactive(self.__down_gpio_line)

        self.__initialized = True

        self.__logger.info(
            "Initialized control with GPIO lines [up %d, down %d] and with "
            + "moving duration %d ms and cool down duration %d ms.",
            self.__up_gpio_line,
            self.__down_gpio_line,
            self.__moving_duration_ms,
            self.__cool_down_duration_ms,
        )

        return True

    def uninitialize(self) -> bool:
        """Uninitialize the control after use."""
        if self.__initialized == False:
            self.__logger.error(
                "Tried to uninitialize control, but it's already "
                + "uninitialized."
            )
            return False

        # Try to release both GPIO lines.
        release_failed = False

        if (
            self.__gpio_manager.release_output_line(self.__up_gpio_line)
            == False
        ):
            self.__logger.error("Failed to release up GPIO line.")
            release_failed = True

        if (
            self.__gpio_manager.release_output_line(self.__down_gpio_line)
            == False
        ):
            self.__logger.error("Failed to release down GPIO line.")
            release_failed = True

        self.__initialized = False

        if release_failed == True:
            return False

        return True

    def get_state(self) -> ControlState:
        """Get the current state."""
        return self.__state

    def set_desired_state(self, state: ControlState) -> None:
        """Set the next state."""
        if self.__initialized == False:
            raise ValueError(
                "Attempted to set state on an uninitialized control."
            )

        if state == ControlState.COOL_DOWN:
            return

        self.__desired_state = state

        self.__logger.info(
            "Set desired state to '%s'.", _state_names[state.value]
        )

    def process(self, notifications: list[str]) -> None:
        """Process the control."""
        if self.__initialized == False:
            raise ValueError("Attempted to process an uninitialized control.")

        if self.__state == ControlState.IDLE:
            self.__process_idle_state(notifications)
            return

        if (self.__state == ControlState.MOVE_UP) or (
            self.__state == ControlState.MOVE_DOWN
        ):
            self.__process_moving_states(notifications)
            return

        if self.__state == ControlState.COOL_DOWN:
            self.__process_cool_down_state(notifications)
            return

        self.__logger.warning(
            "Unhandled state '%s'.", _state_names[self.__state.value]
        )

    def __set_state(
        self, notifications: list[str], state: ControlState
    ) -> None:
        """Trigger a state transition."""
        self.__logger.info(
            "State transition from '%s' to '%s'.",
            _state_names[self.__state.value],
            _state_names[state.value],
        )

        match state:
            case ControlState.MOVE_UP:
                self.__gpio_manager.set_line_inactive(self.__down_gpio_line)
                self.__gpio_manager.set_line_active(self.__up_gpio_line)
                notifications.append(f"Raising the {self.__name}.")

            case ControlState.MOVE_DOWN:
                self.__gpio_manager.set_line_inactive(self.__up_gpio_line)
                self.__gpio_manager.set_line_active(self.__down_gpio_line)
                notifications.append(f"Lowering the {self.__name}.")

            case ControlState.COOL_DOWN:
                self.__gpio_manager.set_line_inactive(self.__up_gpio_line)
                self.__gpio_manager.set_line_inactive(self.__down_gpio_line)
                notifications.append(f"{self.__name} stopped.")

            case _:
                self.__gpio_manager.set_line_inactive(self.__up_gpio_line)
                self.__gpio_manager.set_line_inactive(self.__down_gpio_line)

        self.__state = state
        self.__state_start_time = self.__timer.get_current_time()

    def __process_idle_state(self, notifications: list[str]) -> None:
        """Process the idle state."""
        if self.__desired_state == ControlState.IDLE:
            return

        # Only transitions to moving up or down are allowed.
        if (self.__desired_state != ControlState.MOVE_UP) and (
            self.__desired_state != ControlState.MOVE_DOWN
        ):
            self.__desired_state = ControlState.IDLE
            return

        self.__set_state(notifications, self.__desired_state)

    def __process_moving_states(self, notifications: list[str]) -> None:
        """Process the moving states."""
        # Allow immediate transitions to idle or the other moving state.
        if self.__desired_state != self.__state:
            if self.__desired_state in [
                ControlState.MOVE_UP,
                ControlState.MOVE_DOWN,
            ]:
                self.__set_state(notifications, self.__desired_state)
                return

            if self.__desired_state == ControlState.IDLE:
                self.__set_state(notifications, ControlState.COOL_DOWN)
                return

        # Otherwise automatically transition when the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__state_start_time
        )

        if elapsed_time_ms < self.__moving_duration_ms:
            return

        self.__desired_state = ControlState.IDLE
        self.__set_state(notifications, ControlState.COOL_DOWN)

    def __process_cool_down_state(self, notifications: list[str]) -> None:
        """Process the cool down state."""
        # Automatically transition when the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__state_start_time
        )

        if elapsed_time_ms < self.__cool_down_duration_ms:
            return

        self.__desired_state = ControlState.IDLE
        self.__set_state(notifications, ControlState.IDLE)

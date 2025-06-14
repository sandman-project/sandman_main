"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import enum
import logging

from sandman_main import timer


@enum.unique
class ControlState(enum.Enum):
    """The various states a control can be in."""

    IDLE = 0
    MOVE_UP = 1
    MOVE_DOWN = 2
    COOL_DOWN = 3

    @property
    def label(self) -> str:
        match self:
            case self.IDLE     : return "idle"
            case self.MOVE_UP  : return "move up"
            case self.MOVE_DOWN: return "move down"
            case self.COOL_DOWN: return "cool down"

class Control:
    """The state and logic for a control that manages a part of the bed."""

    def __init__(
        self,
        name: str,
        timer: timer.Timer,
        moving_duration_ms: int,
        cool_down_duration_ms: int,
    ) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = ControlState.IDLE
        self.__desired_state = ControlState.IDLE
        self.__name = name
        self.__timer = timer
        self.__moving_duration_ms = moving_duration_ms
        self.__cool_down_duration_ms = cool_down_duration_ms

        self.__logger.info(
            "Initialized control with moving duration %d ms and cool down "
            + "duration %d ms.",
            self.__moving_duration_ms,
            self.__cool_down_duration_ms,
        )

    def get_state(self) -> ControlState:
        """Get the current state."""
        return self.__state

    def set_desired_state(self, state: ControlState) -> None:
        """Set the next state."""
        if state == ControlState.COOL_DOWN:
            return

        self.__desired_state = state

        self.__logger.info(
            "Set desired state to '%s'.", state.label
        )

    def process(self, notifications: list[str]) -> None:
        """Process the control."""
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
            "Unhandled state '%s'.", self.__state.label
        )

    def __set_state(
        self, notifications: list[str], state: ControlState
    ) -> None:
        """Trigger a state transition."""
        self.__logger.info(
            "State transition from '%s' to '%s'.",
            self.__state.label,
            state.label,
        )

        if state == ControlState.MOVE_UP:
            notifications.append(f"Raising the {self.__name}.")

        elif state == ControlState.MOVE_DOWN:
            notifications.append(f"Lowering the {self.__name}.")

        elif state == ControlState.COOL_DOWN:
            notifications.append(f"{self.__name} stopped.")

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

"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import collections.abc
import enum
import logging
import typing

import timing


class Control:
    """The state and logic for a control that manages a part of the bed."""

    @enum.unique
    class Type(enum.StrEnum):
        """Value indicating a known name of the type of control."""

        BACK = "back"
        LEGS = "legs"
        ELEVATION = "elevation"

    Name: typing.TypeAlias = Type | str
    """String-like value indicating the name of a type of control."""

    @enum.unique
    class State(enum.Enum):
        """The various states a control can be in."""

        IDLE = enum.auto()
        MOVE_UP = enum.auto()
        MOVE_DOWN = enum.auto()
        COOL_DOWN = enum.auto()

        @property
        def label(self) -> str:
            """Human readable phrase describing the control state."""
            match self:
                case self.IDLE:
                    return "idle"
                case self.MOVE_UP:
                    return "move up"
                case self.MOVE_DOWN:
                    return "move down"
                case self.COOL_DOWN:
                    return "cool down"
                case unknown:
                    typing.assert_never(unknown)

    def __init__(
        self,
        name: Name,
        timer: timing.Timer,
        moving_duration_ms: int,
        cool_down_duration_ms: int,
    ) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = Control.State.IDLE
        self.__desired_state = Control.State.IDLE
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

    @property
    def name(self) -> Name:
        """Get the name."""
        return self.__name

    @property
    def state(self) -> State:
        """Get the current state."""
        return self.__state

    def set_desired_state(self, state: State) -> None:
        """Set the next state."""
        if state == Control.State.COOL_DOWN:
            return

        self.__desired_state = state

        self.__logger.info("Set desired state to '%s'.", state.label)

    def process(
        self, notifications: collections.abc.MutableSequence[str]
    ) -> None:
        """Process the control."""
        match self.__state:
            case Control.State.IDLE:
                self.__process_idle_state(notifications)
            case Control.State.MOVE_UP | Control.State.MOVE_DOWN:
                self.__process_moving_states(notifications)
            case Control.State.COOL_DOWN:
                self.__process_cool_down_state(notifications)
            case unknown:
                self.__logger.error(
                    "Unhandled state '%s'.", self.__state.label
                )
                typing.assert_never(unknown)

    def __set_state(
        self, notifications: collections.abc.MutableSequence[str], state: State
    ) -> None:
        """Trigger a state transition."""
        self.__logger.info(
            "State transition from '%s' to '%s'.",
            self.__state.label,
            state.label,
        )

        match state:
            case Control.State.MOVE_UP:
                notifications.append(f"Raising the {self.__name}.")
            case Control.State.MOVE_DOWN:
                notifications.append(f"Lowering the {self.__name}.")
            case Control.State.COOL_DOWN:
                notifications.append(f"{self.__name} stopped.")

        self.__state = state
        self.__state_start_time = self.__timer.get_current_time()

    def __process_idle_state(
        self, notifications: collections.abc.MutableSequence[str]
    ) -> None:
        """Process the idle state."""
        if self.__desired_state == Control.State.IDLE:
            return

        # Only transitions to moving up or down are allowed.
        if (self.__desired_state != Control.State.MOVE_UP) and (
            self.__desired_state != Control.State.MOVE_DOWN
        ):
            self.__desired_state = Control.State.IDLE
            return

        self.__set_state(notifications, self.__desired_state)

    def __process_moving_states(
        self, notifications: collections.abc.MutableSequence[str]
    ) -> None:
        """Process the moving states."""
        # Allow immediate transitions to idle or the other moving state.
        if self.__desired_state != self.__state:
            match self.__desired_state:
                case Control.State.MOVE_UP | Control.State.MOVE_DOWN:
                    self.__set_state(notifications, self.__desired_state)
                    return
                case Control.State.IDLE:
                    self.__set_state(notifications, Control.State.COOL_DOWN)
                    return

        # Otherwise automatically transition when the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__state_start_time
        )

        if elapsed_time_ms < self.__moving_duration_ms:
            return

        self.__desired_state = Control.State.IDLE
        self.__set_state(notifications, Control.State.COOL_DOWN)

    def __process_cool_down_state(
        self, notifications: collections.abc.MutableSequence[str]
    ) -> None:
        """Process the cool down state."""
        # Automatically transition when the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__state_start_time
        )

        if elapsed_time_ms < self.__cool_down_duration_ms:
            return

        self.__desired_state = Control.State.IDLE
        self.__set_state(notifications, Control.State.IDLE)

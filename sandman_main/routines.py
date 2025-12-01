"""Everything needed to support routines.

Routines are user specified sequences of actions.
"""

import logging
import pathlib

from . import controls

_logger = logging.getLogger("sandman.routines")


class RoutineDesc:
    """Describes a routine."""

    class Step:
        """Describes a step of a routine."""

        def __init__(self) -> None:
            """Initialize the step."""
            self.__delay_ms = -1
            self.__control_name = ""
            self.__control_state = controls.Control.State.IDLE

        @property
        def delay_ms(self) -> int:
            """Get the delay."""
            return self.__delay_ms

        @delay_ms.setter
        def delay_ms(self, delay_ms: int) -> None:
            """Set the delay."""
            if isinstance(delay_ms, int) == False:
                raise TypeError("Delay must be an integer.")

            if delay_ms < 0:
                raise ValueError("Cannot set a negative delay.")

            self.__delay_ms = delay_ms

        @property
        def control_name(self) -> str:
            """Get the control name."""
            return self.__control_name

        @control_name.setter
        def control_name(self, name: str) -> None:
            """Set the control name."""
            if isinstance(name, str) == False:
                raise TypeError("Control name must be a string.")

            if name == "":
                raise ValueError("Cannot set an empty control name.")

            self.__control_name = name

        @property
        def control_state(self) -> controls.Control.State:
            """Get the control state."""
            return self.__control_state

        @control_state.setter
        def control_state(self, state: controls.Control.State) -> None:
            """Set the control state."""
            if isinstance(state, controls.Control.State) == False:
                raise TypeError("Control state must be a state.")

            if (state != controls.Control.State.MOVE_UP) and (
                state != controls.Control.State.MOVE_DOWN
            ):
                raise ValueError(
                    "Control state must be either move up or move down."
                )

            self.__control_state = state

        def is_valid(self) -> bool:
            """Check whether this is a valid step."""
            if self.__delay_ms < 0:
                return False

            if self.__control_name == "":
                return False

            if self.__control_state == controls.Control.State.IDLE:
                return False

            return True

    def __init__(self) -> None:
        """Initialize the description."""
        self.__name: str = ""
        self.__is_looping = False

    @property
    def name(self) -> str:
        """Get the name."""
        return self.__name

    @name.setter
    def name(self, new_name: str) -> None:
        """Set the name."""
        if isinstance(new_name, str) == False:
            raise TypeError("Name must be a string.")

        if new_name == "":
            raise ValueError("Cannot set an empty name.")

        self.__name = new_name

    @property
    def is_looping(self) -> bool:
        """Get whether the routine is looping."""
        return self.__is_looping

    @is_looping.setter
    def is_looping(self, is_looping: bool) -> None:
        """Set whether the routine is looping."""
        if isinstance(is_looping, bool) == False:
            raise TypeError("Is looping must be a boolean.")

        self.__is_looping = is_looping

    def is_valid(self) -> bool:
        """Check whether this is a valid routine description."""
        if self.__name == "":
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this description and another have equal values."""
        if not isinstance(other, RoutineDesc):
            return NotImplemented

        return self.__name == other.__name


def bootstrap_routines(base_dir: str) -> None:
    """Handle bootstrapping for routines."""
    routines_path = pathlib.Path(base_dir + "routines/")

    if routines_path.exists() == True:
        return

    _logger.info(
        "Creating missing routines directory '%s'.", str(routines_path)
    )

    try:
        routines_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create routines directory '%s'.", str(routines_path)
        )
        return

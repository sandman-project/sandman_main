"""Everything needed to support routines.

Routines are user specified sequences of actions.
"""

import json
import logging
import pathlib
import typing

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

        def __eq__(self, other: object) -> bool:
            """Check whether this step and another have equal values."""
            if not isinstance(other, RoutineDesc.Step):
                return NotImplemented

            return (
                (self.__delay_ms == other.__delay_ms)
                and (self.__control_name == other.__control_name)
                and (self.__control_state == other.__control_state)
            )

        @classmethod
        def load_from_json(
            cls, step_json: dict[str, int | str], filename: str
        ) -> typing.Self:
            """Load the step from a dictionary."""
            step = cls()

            try:
                delay_ms = step_json["delayMS"]

            except KeyError:
                _logger.warning(
                    "Missing 'delay' key in step in routine description file "
                    + "'%s'.",
                    filename,
                )

            else:
                if isinstance(delay_ms, int) == True:
                    try:
                        step.delay_ms = int(delay_ms)

                    except ValueError:
                        _logger.warning(
                            "Invalid delay '%s' in step in routine "
                            + "description file '%s'.",
                            str(delay_ms),
                            filename,
                        )

                else:
                    _logger.warning(
                        "Delay '%s' in step must be an integer in routine "
                        + "description file '%s'.",
                        str(delay_ms),
                        filename,
                    )

            try:
                control_name = step_json["controlName"]

            except KeyError:
                _logger.warning(
                    "Missing 'control name' key in step in routine "
                    + "description file '%s'.",
                    filename,
                )

            else:
                if isinstance(control_name, str) == True:
                    try:
                        step.control_name = str(control_name)

                    except ValueError:
                        _logger.warning(
                            "Invalid control name '%s' in step in routine "
                            + "description file '%s'.",
                            str(control_name),
                            filename,
                        )

                else:
                    _logger.warning(
                        "Control name '%s' in step must be a string in "
                        + "routine description file '%s'.",
                        str(control_name),
                        filename,
                    )

            try:
                control_state = step_json["controlState"]

            except KeyError:
                _logger.warning(
                    "Missing 'control state' key in step in routine "
                    + "description file '%s'.",
                    filename,
                )

            else:
                if isinstance(control_state, str) == True:
                    if control_state == "move up":
                        step.control_state = controls.Control.State.MOVE_UP

                    elif control_state == "move down":
                        step.control_state = controls.Control.State.MOVE_DOWN

                    else:
                        _logger.warning(
                            "Invalid control state '%s' in step in routine "
                            + "description file '%s'.",
                            str(control_state),
                            filename,
                        )

                else:
                    _logger.warning(
                        "Control state '%s' in step must be a string in "
                        + "routine description file '%s'.",
                        str(control_state),
                        filename,
                    )

            return step

    def __init__(self) -> None:
        """Initialize the description."""
        self.__name: str = ""
        self.__is_looping = False
        self.__steps: list[RoutineDesc.Step] = []

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

    @property
    def steps(self) -> list[Step]:
        """Get the steps."""
        return self.__steps

    def append_step(self, step: Step) -> None:
        """Add a new step to the end."""
        if step.is_valid() == False:
            raise ValueError("Cannot append an invalid step.")

        self.__steps.append(step)

    def is_valid(self) -> bool:
        """Check whether this is a valid routine description."""
        if self.__name == "":
            return False

        for step in self.__steps:
            if step.is_valid() == False:
                return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this description and another have equal values."""
        if not isinstance(other, RoutineDesc):
            return NotImplemented

        return (
            (self.__name == other.__name)
            and (self.__is_looping == other.__is_looping)
            and (self.__steps == other.__steps)
        )

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse a description from a file."""
        desc = cls()

        try:
            with open(filename) as file:
                try:
                    desc_json = json.load(file)

                except json.JSONDecodeError:
                    _logger.error(
                        "JSON error decoding routine description file '%s'.",
                        filename,
                    )
                    return desc

                try:
                    desc.name = desc_json["name"]

                except KeyError:
                    _logger.warning(
                        "Missing 'name' key in routine description file '%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid name '%s' in routine description file '%s'.",
                        str(desc_json["name"]),
                        filename,
                    )

                try:
                    desc.is_looping = desc_json["isLooping"]

                except KeyError:
                    # This is not an error.
                    pass

                except TypeError:
                    _logger.warning(
                        "Invalid looping '%s' in routine description file"
                        + " '%s'.",
                        str(desc_json["isLooping"]),
                        filename,
                    )

                try:
                    steps = desc_json["steps"]

                except KeyError:
                    # This is not an error.
                    pass

                else:
                    try:
                        desc.__load_steps(steps, filename)

                    except TypeError:
                        _logger.warning(
                            "Steps in routine description file '%s' is not a "
                            + "list.",
                            filename,
                        )

        except FileNotFoundError as error:
            _logger.error(
                "Could not find routine description file '%s'.", filename
            )
            raise error

        return desc

    def __load_steps(
        self, steps_json: list[dict[str, int | str]], filename: str
    ) -> None:
        """Load steps."""
        if isinstance(steps_json, list) == False:
            raise TypeError("Routine steps must be a list.")

        for step_json in steps_json:
            step = RoutineDesc.Step.load_from_json(step_json, filename)

            if step.is_valid() == True:
                self.append_step(step)


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

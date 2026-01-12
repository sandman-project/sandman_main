"""Everything needed to support routines.

Routines are user specified sequences of actions.
"""

import json
import logging
import pathlib
import typing

from . import commands, time_util

_logger = logging.getLogger("sandman.routines")


class RoutineDesc:
    """Describes a routine."""

    class Step:
        """Describes a step of a routine."""

        def __init__(self) -> None:
            """Initialize the step."""
            self.__delay_ms = -1
            self.__control_name = ""
            self.__move_direction = commands.MoveControlCommand.Direction.UP

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
        def move_direction(self) -> commands.MoveControlCommand.Direction:
            """Get the move direction."""
            return self.__move_direction

        @move_direction.setter
        def move_direction(
            self, direction: commands.MoveControlCommand.Direction
        ) -> None:
            """Set the move direction."""
            if (
                isinstance(direction, commands.MoveControlCommand.Direction)
                == False
            ):
                raise TypeError("Move direction must be a direction.")

            self.__move_direction = direction

        def is_valid(self) -> bool:
            """Check whether this is a valid step."""
            if self.__delay_ms < 0:
                return False

            if self.__control_name == "":
                return False

            return True

        def __eq__(self, other: object) -> bool:
            """Check whether this step and another have equal values."""
            if not isinstance(other, RoutineDesc.Step):
                return NotImplemented

            return (
                (self.__delay_ms == other.__delay_ms)
                and (self.__control_name == other.__control_name)
                and (self.__move_direction == other.__move_direction)
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
                move_direction = step_json["moveDirection"]

            except KeyError:
                _logger.warning(
                    "Missing 'move direction' key in step in routine "
                    + "description file '%s'.",
                    filename,
                )

            else:
                if isinstance(move_direction, str) == True:
                    if move_direction == "up":
                        step.move_direction = (
                            commands.MoveControlCommand.Direction.UP
                        )

                    elif move_direction == "down":
                        step.move_direction = (
                            commands.MoveControlCommand.Direction.DOWN
                        )

                    else:
                        _logger.warning(
                            "Invalid move direction '%s' in step in routine "
                            + "description file '%s'.",
                            str(move_direction),
                            filename,
                        )

                else:
                    _logger.warning(
                        "Move direction '%s' in step must be a string in "
                        + "routine description file '%s'.",
                        str(move_direction),
                        filename,
                    )

            return step

        def get_as_json(self) -> dict[str, object]:
            """Get the JSON representation of the step."""
            direction = ""

            if (
                self.__move_direction
                == commands.MoveControlCommand.Direction.UP
            ):
                direction = "up"

            elif (
                self.__move_direction
                == commands.MoveControlCommand.Direction.DOWN
            ):
                direction = "down"

            step_json = {
                "delayMS": self.__delay_ms,
                "controlName": self.__control_name,
                "moveDirection": direction,
            }

            return step_json

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

    def save_to_file(self, filename: str) -> None:
        """Save the description to a file."""
        if self.is_valid() == False:
            _logger.warning(
                "Cannot save invalid routine description to '%s'", filename
            )
            return

        steps_json = []

        for step in self.__steps:
            steps_json.append(step.get_as_json())

        desc_json = {
            "name": self.__name,
            "isLooping": self.__is_looping,
            "steps": steps_json,
        }

        try:
            with open(filename, "w") as file:
                json.dump(desc_json, file, indent=4)

        except OSError as error:
            _logger.error(
                "Failed to open '%s' to save routine description.", filename
            )
            raise error

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


class Routine:
    """An instance of a running routine."""

    def __init__(self, desc: RoutineDesc, timer: time_util.Timer) -> None:
        """Initialize the routine."""
        self.__desc = desc
        self.__timer = timer
        self.__is_finished = False
        self.__step_index = 0
        self.__step_start_time = timer.get_current_time()

    @property
    def is_finished(self) -> bool:
        """Get whether the routine is finished."""
        return self.__is_finished

    def process(self, command_list: list[commands.MoveControlCommand]) -> None:
        """Process the routine."""
        if self.__is_finished == True:
            return

        steps = self.__desc.steps
        num_steps = len(steps)

        if num_steps == 0:
            if self.__desc.is_looping == False:
                self.__is_finished = True

            return

        # Wait until the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__step_start_time
        )

        step = steps[self.__step_index]

        if elapsed_time_ms < step.delay_ms:
            return

        # Execute the step.
        command = commands.MoveControlCommand(
            step.control_name, step.move_direction, "routine"
        )
        command_list.append(command)

        self.__advance_step()

    def __advance_step(self) -> None:
        """Advance to the next step."""
        self.__step_start_time = self.__timer.get_current_time()

        num_steps = len(self.__desc.steps)
        self.__step_index += 1

        if self.__step_index < num_steps:
            return

        # We have reached the end of the routine, so either loop or finish.
        if self.__desc.is_looping == True:
            self.__step_index = 0
            return

        self.__is_finished = True


class RoutineManager:
    """Manages routine descriptions and running routines."""

    def __init__(self, timer: time_util.Timer) -> None:
        """Initialize the manager."""
        self.__timer = timer
        self.__descs: dict[str, RoutineDesc] = {}
        self.__routines: dict[str, Routine] = {}

    @property
    def num_loaded(self) -> int:
        """Get the number of loaded routine descriptions."""
        return len(self.__descs)

    @property
    def num_running(self) -> int:
        """Get the number of running routines."""
        return len(self.__routines)

    def initialize(self) -> None:
        """Initialize the manager (load routine descriptions)."""
        self.uninitialize()

    def uninitialize(self) -> None:
        """Uninitialize the manager."""
        self.__descs.clear()
        self.__routines.clear()


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

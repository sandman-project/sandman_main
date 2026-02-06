"""Everything needed to manage controls.

Controls are used to manipulate parts of the bed.
"""

import enum
import json
import logging
import pathlib
import typing

from . import commands, gpio, reports, time_util

_logger = logging.getLogger("sandman.control_config")


class ControlConfig:
    """Specifies the configuration of a control."""

    def __init__(self) -> None:
        """Initialize the control config."""
        self.__name: str = ""
        self.__up_gpio_line: int = -1
        self.__down_gpio_line: int = -1
        self.__moving_duration_ms: int = -1
        self.__cool_down_duration_ms: int = 25

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
    def up_gpio_line(self) -> int:
        """Get the up GPIO line."""
        return self.__up_gpio_line

    @up_gpio_line.setter
    def up_gpio_line(self, line: int) -> None:
        """Set the up GPIO line."""
        if isinstance(line, int) == False:
            raise TypeError("GPIO line must be an integer.")

        if line < 0:
            raise ValueError("GPIO line cannot be negative.")

        self.__up_gpio_line = line

    @property
    def down_gpio_line(self) -> int:
        """Get the down GPIO line."""
        return self.__down_gpio_line

    @down_gpio_line.setter
    def down_gpio_line(self, line: int) -> None:
        """Set the down GPIO line."""
        if isinstance(line, int) == False:
            raise TypeError("GPIO line must be an integer.")

        if line < 0:
            raise ValueError("GPIO line cannot be negative.")

        self.__down_gpio_line = line

    @property
    def moving_duration_ms(self) -> int:
        """Get the moving duration."""
        return self.__moving_duration_ms

    @moving_duration_ms.setter
    def moving_duration_ms(self, duration_ms: int) -> None:
        """Set the moving duration."""
        if isinstance(duration_ms, int) == False:
            raise TypeError("Duration must be an integer.")

        if duration_ms < 0:
            raise ValueError("Duration cannot be negative.")

        self.__moving_duration_ms = duration_ms

    @property
    def cool_down_duration_ms(self) -> int:
        """Get the cool down duration."""
        return self.__cool_down_duration_ms

    @cool_down_duration_ms.setter
    def cool_down_duration_ms(self, duration_ms: int) -> None:
        """Set the cool down duration."""
        if isinstance(duration_ms, int) == False:
            raise TypeError("Duration must be an integer.")

        if duration_ms < 0:
            raise ValueError("Duration cannot be negative.")

        self.__cool_down_duration_ms = duration_ms

    def is_valid(self) -> bool:
        """Check whether this is a valid control config."""
        if self.__name == "":
            return False

        if self.__up_gpio_line < 0:
            return False

        if self.__down_gpio_line < 0:
            return False

        # GPIO lines cannot be the same.
        if self.__up_gpio_line == self.__down_gpio_line:
            return False

        if self.__moving_duration_ms < 0:
            return False

        if self.__cool_down_duration_ms < 0:
            return False

        return True

    def __eq__(self, other: object) -> bool:
        """Check whether this config and another have equal values."""
        if not isinstance(other, ControlConfig):
            return NotImplemented

        return (
            (self.__name == other.__name)
            and (self.__up_gpio_line == other.__up_gpio_line)
            and (self.__down_gpio_line == other.__down_gpio_line)
            and (self.__moving_duration_ms == other.__moving_duration_ms)
            and (self.__cool_down_duration_ms == other.__cool_down_duration_ms)
        )

    @classmethod
    def parse_from_file(cls, filename: str) -> typing.Self:
        """Parse a config from a file."""
        config = cls()

        try:
            with open(filename) as file:
                try:
                    config_json = json.load(file)

                except json.JSONDecodeError:
                    _logger.error(
                        "JSON error decoding control config file '%s'.",
                        filename,
                    )
                    return config

                try:
                    config.name = config_json["name"]

                except KeyError:
                    _logger.warning(
                        "Missing 'name' key in control config file '%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid name '%s' in control config file '%s'.",
                        str(config_json["name"]),
                        filename,
                    )

                try:
                    config.up_gpio_line = config_json["upGPIOLine"]

                except KeyError:
                    _logger.warning(
                        "Missing 'up GPIO line' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid up GPIO line '%s' in control config file "
                        + "'%s'.",
                        str(config_json["upGPIOLine"]),
                        filename,
                    )

                try:
                    config.down_gpio_line = config_json["downGPIOLine"]

                except KeyError:
                    _logger.warning(
                        "Missing 'down GPIO line' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid down GPIO line '%s' in control config file "
                        + "'%s'.",
                        str(config_json["downGPIOLine"]),
                        filename,
                    )

                try:
                    config.moving_duration_ms = config_json["movingDurationMS"]

                except KeyError:
                    _logger.warning(
                        "Missing 'moving duration' key in control config file "
                        + "'%s'.",
                        filename,
                    )

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid moving duration '%s' in control config file "
                        + "'%s'.",
                        str(config_json["movingDurationMS"]),
                        filename,
                    )

                try:
                    config.cool_down_duration_ms = config_json[
                        "coolDownDurationMS"
                    ]

                except KeyError:
                    # This is acceptable.
                    pass

                except (TypeError, ValueError):
                    _logger.warning(
                        "Invalid cool down duration '%s' in control config "
                        + "file '%s'.",
                        str(config_json["coolDownDurationMS"]),
                        filename,
                    )

        except FileNotFoundError as error:
            _logger.error("Could not find control config file '%s'.", filename)
            raise error

        return config

    def save_to_file(self, filename: str) -> None:
        """Save a config to a file."""
        if self.is_valid() == False:
            _logger.warning(
                "Cannot save invalid control config to '%s'", filename
            )
            return

        config_json = {
            "name": self.__name,
            "upGPIOLine": self.__up_gpio_line,
            "downGPIOLine": self.__down_gpio_line,
            "movingDurationMS": self.__moving_duration_ms,
            "coolDownDurationMS": self.__cool_down_duration_ms,
        }

        try:
            with open(filename, "w") as file:
                json.dump(config_json, file, indent=4)

        except OSError as error:
            _logger.error(
                "Failed to open '%s' to save control config.", filename
            )
            raise error


class Control:
    """The state and logic for a control that manages a part of the bed."""

    @enum.unique
    class State(enum.Enum):
        """The various states a control can be in."""

        IDLE = enum.auto()
        MOVE_UP = enum.auto()
        MOVE_DOWN = enum.auto()
        COOL_DOWN = enum.auto()

        def as_string(self) -> str:
            """Return a readable phrase describing the control state."""
            match self:
                case Control.State.IDLE:
                    return "idle"
                case Control.State.MOVE_UP:
                    return "move up"
                case Control.State.MOVE_DOWN:
                    return "move down"
                case Control.State.COOL_DOWN:
                    return "cool down"
                case _:
                    typing.assert_never(self)

    def __init__(
        self,
        name: str,
        timer: time_util.Timer,
        gpio_manager: gpio.GPIOManager,
    ) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.control." + name)
        self.__state = Control.State.IDLE
        self.__desired_state = Control.State.IDLE
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

    @property
    def state(self) -> State:
        """Get the current state."""
        return self.__state

    def set_desired_state(self, state: State) -> None:
        """Set the next state."""
        if self.__initialized == False:
            raise ValueError(
                "Attempted to set state on an uninitialized control."
            )

        if state == Control.State.COOL_DOWN:
            return

        self.__desired_state = state

        self.__logger.info("Set desired state to '%s'.", state.as_string())

    def process(self, notifications: list[str]) -> None:
        """Process the control."""
        if self.__initialized == False:
            raise ValueError("Attempted to process an uninitialized control.")

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

    def __set_state(self, notifications: list[str], state: State) -> None:
        """Trigger a state transition."""
        self.__logger.info(
            "State transition from '%s' to '%s'.",
            self.__state.as_string(),
            state.as_string(),
        )

        match state:
            case Control.State.MOVE_UP:
                self.__gpio_manager.set_line_inactive(self.__down_gpio_line)
                self.__gpio_manager.set_line_active(self.__up_gpio_line)
                notifications.append(f"Raising the {self.__name}.")

            case Control.State.MOVE_DOWN:
                self.__gpio_manager.set_line_inactive(self.__up_gpio_line)
                self.__gpio_manager.set_line_active(self.__down_gpio_line)
                notifications.append(f"Lowering the {self.__name}.")

            case Control.State.COOL_DOWN:
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
        if self.__desired_state == Control.State.IDLE:
            return

        # Only transitions to moving up or down are allowed.
        if (self.__desired_state != Control.State.MOVE_UP) and (
            self.__desired_state != Control.State.MOVE_DOWN
        ):
            self.__desired_state = Control.State.IDLE
            return

        self.__set_state(notifications, self.__desired_state)

    def __process_moving_states(self, notifications: list[str]) -> None:
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

    def __process_cool_down_state(self, notifications: list[str]) -> None:
        """Process the cool down state."""
        # Automatically transition when the time is up.
        elapsed_time_ms = self.__timer.get_time_since_ms(
            self.__state_start_time
        )

        if elapsed_time_ms < self.__cool_down_duration_ms:
            return

        self.__desired_state = Control.State.IDLE
        self.__set_state(notifications, Control.State.IDLE)


class ControlManager:
    """Manages controls."""

    def __init__(
        self,
        timer: time_util.Timer,
        gpio_manager: gpio.GPIOManager,
        report_manager: reports.ReportManager,
    ) -> None:
        """Initialize the manager."""
        self.__timer = timer
        self.__gpio_manager = gpio_manager
        self.__report_manager = report_manager
        self.__controls: dict[str, Control] = {}

    @property
    def num_controls(self) -> int:
        """Get the number of controls."""
        return len(self.__controls)

    def get_states(self) -> dict[str, Control.State]:
        """Get the states of the controls."""
        states: dict[str, Control.State] = {}

        for name, control in self.__controls.items():
            states[name] = control.state

        return states

    def initialize(self, base_dir: str) -> None:
        """Initialize the manager (load controls)."""
        self.uninitialize()

        control_path = pathlib.Path(base_dir + "controls/")
        _logger.info("Loading controls from '%s'.", str(control_path))

        for config_path in control_path.glob("*.ctl"):
            # Try parsing the config.
            config_file = str(config_path)
            _logger.info("Loading control from '%s'.", config_file)

            config = ControlConfig.parse_from_file(config_file)

            if config.is_valid() == False:
                continue

            # Make sure it control with this name doesn't already exist.
            if config.name in self.__controls:
                _logger.warning(
                    "A control with name '%s' already exists. Ignoring new "
                    + "config.",
                    config.name,
                )
                continue

            control = Control(config.name, self.__timer, self.__gpio_manager)

            if (
                control.initialize(
                    up_gpio_line=config.up_gpio_line,
                    down_gpio_line=config.down_gpio_line,
                    moving_duration_ms=config.moving_duration_ms,
                    cool_down_duration_ms=config.cool_down_duration_ms,
                )
                == False
            ):
                continue

            self.__controls[config.name] = control

    def uninitialize(self) -> None:
        """Uninitialize the manager."""
        for _name, control in self.__controls.items():
            control.uninitialize()

        self.__controls.clear()

    def process_command(self, command: commands.ControlCommand) -> bool:
        """Process a control command.

        Returns whether the command was successful.
        """
        # See if we have a control with a matching name.
        try:
            control = self.__controls[command.control_name]

        except KeyError:
            _logger.warning(
                "No control with name '%s' found.", command.control_name
            )
            return False

        match command.direction:
            case commands.ControlCommand.Direction.UP:
                control.set_desired_state(Control.State.MOVE_UP)
                self.__report_manager.add_control_event(
                    command.control_name,
                    command.direction.as_string(),
                    command.source,
                )

            case commands.ControlCommand.Direction.DOWN:
                control.set_desired_state(Control.State.MOVE_DOWN)
                self.__report_manager.add_control_event(
                    command.control_name,
                    command.direction.as_string(),
                    command.source,
                )

            case unknown:
                typing.assert_never(unknown)

        return True


def bootstrap_controls(base_dir: str) -> None:
    """Handle bootstrapping for controls."""
    control_path = pathlib.Path(base_dir + "controls/")

    if control_path.exists() == True:
        return

    _logger.info(
        "Creating missing control config directory '%s'.", str(control_path)
    )

    try:
        control_path.mkdir()

    except Exception:
        _logger.warning(
            "Failed to create control config directory '%s'.",
            str(control_path),
        )
        return

    # Now that the directory exists, populate it with some default controls.
    back_config = ControlConfig()
    back_config.name = "back"
    back_config.up_gpio_line = 20
    back_config.down_gpio_line = 16
    back_config.moving_duration_ms = 7000

    back_config.save_to_file(str(control_path) + "/back.ctl")

    legs_config = ControlConfig()
    legs_config.name = "legs"
    legs_config.up_gpio_line = 13
    legs_config.down_gpio_line = 26
    legs_config.moving_duration_ms = 4000

    legs_config.save_to_file(str(control_path) + "/legs.ctl")

    elevation_config = ControlConfig()
    elevation_config.name = "elevation"
    elevation_config.up_gpio_line = 5
    elevation_config.down_gpio_line = 19
    elevation_config.moving_duration_ms = 4000

    elevation_config.save_to_file(str(control_path) + "/elevation.ctl")

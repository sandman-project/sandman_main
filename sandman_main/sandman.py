"""Entry point for the Sandman application."""

import logging
import logging.handlers
import pathlib
import time
import typing

from . import (
    commands,
    control_configs,
    controls,
    gpio,
    mqtt,
    reports,
    routines,
    setting,
    time_util,
)


class Sandman:
    """The state and logic to run the Sandman application."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__timer = time_util.Timer()
        self.__time_source = time_util.TimeSource()
        # Change this if you want to run off device.
        self.__gpio_manager = gpio.GPIOManager(is_live_mode=True)
        self.__controls: dict[str, controls.Control] = {}

    def __setup_logging(self) -> None:
        """Set up logging."""
        logger = logging.getLogger("sandman")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s: %(message)s"
        )

        file_handler = logging.handlers.RotatingFileHandler(
            self.__base_dir + "sandman.log", backupCount=10, maxBytes=1000000
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        self.__logger = logger

    def initialize(self, options: dict[str, typing.Any] | None = None) -> bool:
        """Initialize the app.

        Returns True if initialization was successful, False otherwise.
        """
        self.__is_testing = False
        self.__base_dir = str(pathlib.Path.home()) + "/.sandman/"

        if options is not None:
            if "TESTING" in options:
                self.__is_testing = options["TESTING"]

            if "BASE_DIR" in options:
                self.__base_dir = options["BASE_DIR"]

        base_path = pathlib.Path(self.__base_dir)

        # If the base directory doesn't exist, try to create it.
        base_dir_exists = base_path.exists()

        if base_dir_exists == False:
            try:
                base_path.mkdir()
            except Exception:
                print(f"Failed to create base directory '{self.__base_dir}'")
                return False

        # Now that we have a base directory, set up logging.
        self.__setup_logging()

        self.__gpio_manager.initialize()

        # We only bootstrap once.
        setting.bootstrap_settings(self.__base_dir)
        control_configs.bootstrap_control_configs(self.__base_dir)
        reports.bootstrap_reports(self.__base_dir)
        routines.bootstrap_routines(self.__base_dir)

        self.__settings = setting.Settings.parse_from_file(
            self.__base_dir + "settings.cfg"
        )
        self.__time_source.set_time_zone_name(self.__settings.time_zone_name)

        self.__report_manager = reports.ReportManager(
            self.__time_source, self.__base_dir
        )

        self.__routine_manager = routines.RoutineManager(
            self.__timer, self.__report_manager
        )
        return True

    def run(self) -> None:
        """Run the program."""
        self.__logger.info("Starting Sandman...")

        self.__initialize_controls()
        self.__routine_manager.initialize(self.__base_dir)

        self.__mqtt_client = mqtt.MQTTClient()

        if self.__mqtt_client.connect() == False:
            return

        if self.__mqtt_client.start() == False:
            return

        self.__mqtt_client.play_notification("Sandman initialized.")

        try:
            while True:
                self.__process()

                # Sleep for 10 µs.
                time.sleep(0.01)

        except KeyboardInterrupt:
            pass

        self.__mqtt_client.stop()

        self.__logger.info("Sandman exiting.")

        self.__routine_manager.uninitialize()

        # Uninitialize the controls.
        self.__uninitialize_controls()

        self.__gpio_manager.uninitialize()

    def is_testing(self) -> bool:
        """Return whether the app is in test mode."""
        return self.__is_testing

    def __initialize_controls(self) -> None:
        """Initialize the controls."""
        # If there are existing controls, uninitialize them.
        self.__uninitialize_controls()

        control_path = pathlib.Path(self.__base_dir + "controls/")
        self.__logger.info("Loading controls from '%s'.", str(control_path))

        for config_path in control_path.glob("*.ctl"):
            # Try parsing the config.
            config_file = str(config_path)
            self.__logger.info("Loading control from '%s'.", config_file)

            config = control_configs.ControlConfig.parse_from_file(config_file)

            if config.is_valid() == False:
                continue

            # Make sure it control with this name doesn't already exist.
            if config.name in self.__controls:
                self.__logger.warning(
                    "A control with name '%s' already exists. Ignoring new "
                    + "config.",
                    config.name,
                )
                continue

            control = controls.Control(
                config.name, self.__timer, self.__gpio_manager
            )

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

    def __uninitialize_controls(self) -> None:
        """Uninitialize the controls."""
        for _name, control in self.__controls.items():
            control.uninitialize()

        self.__controls.clear()

    def __process(self) -> None:
        """Process during the main loop."""
        command_list: list[
            commands.StatusCommand
            | commands.MoveControlCommand
            | commands.RoutineCommand
        ] = []
        notification_list: list[str] = []

        self.__routine_manager.process_routines(
            command_list, notification_list
        )

        # Fetch any commands from MQTT as well.
        command = self.__mqtt_client.pop_command()

        while command is not None:
            command_list.append(command)

            command = self.__mqtt_client.pop_command()

        self.__process_commands(notification_list, command_list)

        self.__process_controls(notification_list)

        self.__mqtt_client.process()
        self.__report_manager.process()

        # Play all the notifications.
        for notification in notification_list:
            self.__mqtt_client.play_notification(notification)

    def __process_commands(
        self,
        notification_list: list[str],
        command_list: list[
            commands.StatusCommand
            | commands.MoveControlCommand
            | commands.RoutineCommand
        ],
    ) -> None:
        """Process pending commands."""
        for command in command_list:
            match command:
                case commands.StatusCommand():
                    self.__process_status_command(notification_list)

                case commands.MoveControlCommand():
                    self.__process_move_control_command(command)

                case commands.RoutineCommand():
                    notification = self.__routine_manager.process_command(
                        command
                    )

                    if notification != "":
                        notification_list.append(notification)

                case unknown:
                    typing.assert_never(unknown)

    def __process_status_command(self, notification_list: list[str]) -> None:
        """Process a status command."""
        self.__report_manager.add_status_event()

        notification_list.append("Sandman is running.")

        # Add a notification for each running routine.
        running_names = self.__routine_manager.get_running_names()

        for name in running_names:
            notification_list.append(f"The {name} routine is running.")

    def __process_move_control_command(
        self, command: commands.MoveControlCommand
    ) -> None:
        """Process a move control command."""
        # See if we have a control with a matching name.
        try:
            control = self.__controls[command.control_name]

        except KeyError:
            self.__logger.warning(
                "No control with name '%s' found.", command.control_name
            )
            return

        match command.direction:
            case commands.MoveControlCommand.Direction.UP:
                control.set_desired_state(controls.Control.State.MOVE_UP)
                self.__report_manager.add_control_event(
                    command.control_name,
                    command.direction.as_string(),
                    command.source,
                )

            case commands.MoveControlCommand.Direction.DOWN:
                control.set_desired_state(controls.Control.State.MOVE_DOWN)
                self.__report_manager.add_control_event(
                    command.control_name,
                    command.direction.as_string(),
                    command.source,
                )

            case unknown:
                typing.assert_never(unknown)

    def __process_controls(self, notification_list: list[str]) -> None:
        """Process controls."""
        for _name, control in self.__controls.items():
            control.process(notification_list)


def create_app(
    options: dict[str, typing.Any] | None = None,
) -> Sandman | None:
    """Create an instance of the app.

    NOTE - If the options dictionary does not contain a key BASE_DIR, the base
    directory will become ~/.sandman/.
    """
    app = Sandman()

    if app.initialize(options) == False:
        return None

    return app

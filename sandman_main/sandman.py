"""Entry point for the Sandman application."""

import logging
import logging.handlers
import pathlib
import time
import typing

from . import (
    commands,
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
        controls.bootstrap_controls(self.__base_dir)
        reports.bootstrap_reports(self.__base_dir)
        routines.bootstrap_routines(self.__base_dir)

        self.__settings = setting.Settings.parse_from_file(
            self.__base_dir + "settings.cfg"
        )
        self.__time_source.set_time_zone_name(self.__settings.time_zone_name)

        self.__report_manager = reports.ReportManager(
            self.__time_source, self.__base_dir
        )

        self.__control_manager = controls.ControlManager(
            self.__timer, self.__gpio_manager, self.__report_manager
        )

        self.__routine_manager = routines.RoutineManager(
            self.__timer, self.__report_manager
        )
        return True

    def run(self) -> None:
        """Run the program."""
        self.__logger.info("Starting Sandman...")

        self.__control_manager.initialize(self.__base_dir)
        self.__routine_manager.initialize(self.__base_dir)

        self.__mqtt_client = mqtt.MQTTClient()

        if self.__mqtt_client.connect() == False:
            return

        if self.__mqtt_client.start() == False:
            return

        startup_delay_sec = self.__settings.startup_delay_sec
        self.__logger.info("Sleeping for %i seconds...", startup_delay_sec)
        time.sleep(startup_delay_sec)

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
        self.__control_manager.uninitialize()

        self.__gpio_manager.uninitialize()

    def is_testing(self) -> bool:
        """Return whether the app is in test mode."""
        return self.__is_testing

    def __process(self) -> None:
        """Process during the main loop."""
        command_list: list[
            commands.StatusCommand
            | commands.ControlCommand
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

        self.__control_manager.process_controls(notification_list)

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
            | commands.ControlCommand
            | commands.RoutineCommand
        ],
    ) -> None:
        """Process pending commands."""
        for command in command_list:
            match command:
                case commands.StatusCommand():
                    self.__process_status_command(notification_list)

                case commands.ControlCommand():
                    self.__control_manager.process_command(command)

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

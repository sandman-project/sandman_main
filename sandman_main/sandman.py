"""Entry point for the Sandman application."""

import collections.abc
import logging
import logging.handlers
import pathlib
import time
import typing

import commands
import controls
import mqtt
import timing


class Sandman:
    """The state and logic to run the Sandman application."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__timer = timing.Timer()
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

    def initialize(
        self, options: collections.abc.Mapping[str, typing.Any] | None = None
    ) -> bool:
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

        return True

    def run(self) -> None:
        """Run the program."""
        self.__logger.info("Starting Sandman...")

        # Create some controls (manually for now).
        cool_down_duration_ms = 25

        control_list = (
            controls.Control(
                "back",
                self.__timer,
                moving_duration_ms=7000,
                cool_down_duration_ms=cool_down_duration_ms,
            ),
            controls.Control(
                "legs",
                self.__timer,
                moving_duration_ms=4000,
                cool_down_duration_ms=cool_down_duration_ms,
            ),
            controls.Control(
                "elevation",
                self.__timer,
                moving_duration_ms=4000,
                cool_down_duration_ms=cool_down_duration_ms,
            ),
        )

        self.__controls.update(
            {control.name: control for control in control_list}
        )

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

    def is_testing(self) -> bool:
        """Return whether the app is in test mode."""
        return self.__is_testing

    def __process(self) -> None:
        """Process during the main loop."""
        self.__process_commands()

        self.__process_controls()

        self.__mqtt_client.process()

    def __process_commands(self) -> None:
        """Process pending commands."""
        command = self.__mqtt_client.pop_command()

        while command is not None:
            match command:
                case commands.StatusCommand():
                    self.__mqtt_client.play_notification("Sandman is running.")
                case commands.MoveControlCommand():
                    self.__process_move_control_command(command)
                case unknown:
                    typing.assert_never(unknown)

            command = self.__mqtt_client.pop_command()

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
            case commands.MoveControlCommand.Direction.DOWN:
                control.set_desired_state(controls.Control.State.MOVE_DOWN)
            case unknown:
                typing.assert_never(unknown)

    def __process_controls(self) -> None:
        """Process controls."""
        notifications: list[str] = []

        for _name, control in self.__controls.items():
            control.process(notifications)

        for notification in notifications:
            self.__mqtt_client.play_notification(notification)


def create_app(
    options: collections.abc.Mapping[str, typing.Any] | None = None,
) -> Sandman | None:
    """Create an instance of the app.

    NOTE - If the options dictionary does not contain a key BASE_DIR, the base
    directory will become ~/.sandman/.
    """
    app = Sandman()

    if app.initialize(options) == False:
        return None

    return app


if __name__ == "__main__":
    sandman = create_app()

    if sandman is None:
        raise ValueError("Failed to create Sandman application.")

    sandman.run()

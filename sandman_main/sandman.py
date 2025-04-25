"""Entry point for the Sandman application."""

import logging
import logging.handlers
import pathlib
import time

import commands
import mqtt


class Sandman:
    """The state and logic to run the Sandman application."""

    def __init__(self) -> None:
        """Initialize the instance."""
        pass

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

    def initialize(self, options: dict[any] = None) -> bool:
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

        self.__mqtt_client = mqtt.MQTTClient()

        if self.__mqtt_client.connect() == False:
            return

        if self.__mqtt_client.start() == False:
            return

        while True:
            self.__process_commands()

            # Sleep for 10 µs.
            time.sleep(0.01)

    def is_testing(self) -> bool:
        """Return whether the app is in test mode."""
        return self.__is_testing

    def __process_commands(self) -> None:
        """Process pending commands."""
        command = self.__mqtt_client.pop_command()

        while command is not None:
            if isinstance(command, commands.StatusCommand):
                print("Status command")

            command = self.__mqtt_client.pop_command()


def create_app(options: dict[any] = None) -> Sandman:
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
    sandman.run()

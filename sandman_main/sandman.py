"""Entry point for the Sandman application."""

import logging
import logging.handlers
import pathlib


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

    def run(self) -> None:
        """Run the program."""
        self.__base_dir = str(pathlib.Path.home()) + "/.sandman/"

        base_path = pathlib.Path(self.__base_dir)

        # If the base directory doesn't exist, try to create it.
        base_dir_exists = base_path.exists()

        if base_dir_exists == False:
            try:
                base_path.mkdir()
            except Exception:
                print(f"Failed to create base directory '{self.__base_dir}'")
                return

        # Now that we have a base directory, set up logging.
        self.__setup_logging()

        self.__logger.info("Starting Sandman...")


if __name__ == "__main__":
    sandman = Sandman()
    sandman.run()

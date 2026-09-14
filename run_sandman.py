"""Main entry point for the Sandman application."""

import time

import sandman_main

if __name__ == "__main__":
    app = sandman_main.create_app()

    app.start()

    try:
        while True:
            # Sleep for 10 ms.
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass

    app.stop()

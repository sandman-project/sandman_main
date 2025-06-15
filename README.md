[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sandman-project/sandman_main/main.svg)](https://results.pre-commit.ci/latest/github/sandman-project/sandman_main/main)

# Sandman Main

Sandman main is part of the [Sandman Project](https://github.com/sandman-project), which aims to provide a device that allows hospital style beds to be controlled by voice. This component will provide the main functionality, such as receiving commands, manipulating GPIO to move the bed, and more. However, it is currently being rebuilt from the previous C++ implementation. At the moment, Linux is the only supported operating system.

## License

[MIT](https://choosealicense.com/licenses/mit/)

# Getting Started with Development

[Install `uv`.](https://docs.astral.sh/uv/getting-started/installation/)

```shell
# Create a virtual environment (optional, but recommended).
uv venv

# Install the dependencies.
uv sync

# Run the Sandman application.
# (Assuming that you are at the root of the repository.)
uv run sandman_main/sandman.py

# Run the tests.
uv run pytest
```

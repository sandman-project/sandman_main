[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sandman-project/sandman_main/main.svg)](https://results.pre-commit.ci/latest/github/sandman-project/sandman_main/main)

# Sandman Main

Sandman main is part of the [Sandman Project](https://github.com/sandman-project), which aims to provide a device that allows hospital style beds to be controlled by voice. This component will provide the main functionality, such as receiving commands, manipulating GPIO to move the bed, and more. However, it is currently being rebuilt from the previous C++ implementation. At the moment, Linux is the only supported operating system.

## Rhasspy

Sandman relies on [Rhasspy](https://rhasspy.readthedocs.io) to provide voice control and auditory feedback. It must be set up first in order for Sandman to work. You can find instructions for setting up Rhasspy [here](rhasspy/README.md).

## Sandman Setup

If you are interested in running Sandman in development mode, please read [CONTRIBUTING](CONTRIBUTING.md). If you wish to run it in deployment mode, you can use the following instructions. 

At the moment, in order to for GPIO to work inside the Docker container, we need the group ID in an environment variable. This command will do that:

```bash
export GPIO_GID=$(getent group gpio | cut --delimiter ':' --fields 3)
```

You will have to repeat this command for each shell instance that starts the container. Then,

```bash
cd ~/sandman_main
```
```bash
docker compose up -d
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

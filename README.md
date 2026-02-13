[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sandman-project/sandman_main/main.svg)](https://results.pre-commit.ci/latest/github/sandman-project/sandman_main/main)

# Sandman Main

Sandman main is part of the [Sandman Project](https://github.com/sandman-project), which aims to provide a device that allows hospital style beds to be controlled by voice. This component provides the main functionality, such as receiving commands, manipulating GPIO to move the bed, and more. At the moment, Linux is the only supported operating system.

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

Once Sandman runs for the first time, it will populate ~/.sandman with some files and directories. When it does, it will configure three controls for the bed: one for the back, one for the legs, and one for the elevation, as these are common controls on hospital style beds.

## Using Sandman

Once Sandman is running, it can be controlled by voice. To give Sandman a command, first say the wake word that was configured during Rhasspy setup. Once you hear the sound indicating that the wake word has been recognized, say a command.

### Getting Status

A command such as "get the status" or "what is the status" should cause Sandman to report that it is running and list all of the routines that are currently running.

### Moving The Bed

There are a variety of ways to give a command to move a part of the bed. One of them takes the following form:

[raise|lower] the [part name]

The default configuration has a part for the back, the legs, and the elevation of the bed. So, for example giving the command "lower the back" should cause Sandman to report that the back is lowering. When these commands are given, the bed should move in the specified direction for the amount of time specified in the configuration.

### Using Routines

Commands to start and stop routines take the following form:

[start|stop] the [routine name] routine

After giving a command to start a routine, Sandman should report that the routine started, if it has been defined. If it is already running, it should report that it is already running. After giving a command to stop a routine, Sandman should report that it has been stopped if it was running. If it was not running, it should report that it was not running. There are no routines defined by default.

## License

[MIT](https://choosealicense.com/licenses/mit/)

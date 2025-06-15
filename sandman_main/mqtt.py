"""Everything needed to use MQTT."""

import collections
import dataclasses
import json
import logging
import time
from collections.abc import Mapping
from typing import Any, Protocol

import commands
import paho.mqtt.client
import paho.mqtt.enums
import paho.mqtt.reasoncodes
from commands import MoveControlCommand, StatusCommand


@dataclasses.dataclass
class _MessageInfo:
    """Represents a message that has been received or needs to be sent."""

    topic: str
    payload: str


class MQTTClient:
    """Functionality to communicate with an MQTT broker."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.mqtt_client")
        self.__pending_commands = collections.deque[
            StatusCommand | MoveControlCommand
        ]()
        self.__pending_notifications = collections.deque[str]()
        self.__is_connected: bool = False
        pass

    def connect(self) -> bool:
        """Connect to the broker."""
        self.__client = paho.mqtt.client.Client()

        self.__client.on_connect = self.__handle_connect

        host = "localhost"
        port = 12183

        # Keep attempting to connect a certain number of times before giving
        # up.
        num_attempts = 150

        for attempt_index in range(num_attempts):
            self.__logger.info(
                "Attempting to connect to MQTT host %s:%d (attempt %d)...",
                host,
                port,
                attempt_index + 1,
            )

            try:
                connect_result = self.__client.connect(host, port)
            except Exception as exception:
                self.__logger.error(
                    "Connect raised %s exception: %s",
                    type(exception),
                    exception,
                )
                return False
            else:
                connect_failed = (
                    connect_result
                    != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS
                )

            if connect_failed == False:
                self.__logger.info("Initiated connection to MQTT host.")
                return True

            self.__logger.info(
                "Connection attempt %d to MQTT host failed.", attempt_index + 1
            )

            # Sleep for two seconds.
            time.sleep(2)

        self.__logger.warning(
            "Failed to connect to MQTT host after %d attempts.", num_attempts
        )
        return False

    def start(self) -> bool:
        """Start MQTT services after connecting."""
        if self.__client is None:
            return False

        # Start processing in another thread.
        start_result = self.__client.loop_start()

        if start_result != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            return False

        return True

    def stop(self) -> None:
        """Stop MQTT services."""
        if self.__client is None:
            return

        self.__client.loop_stop()
        self.__client.disconnect()

    def pop_command(self) -> StatusCommand | MoveControlCommand | None:
        """Pop the next pending command off the queue, if there is one.

        Returns the command or None if the queue is empty.
        """
        try:
            command = self.__pending_commands.popleft()
        except IndexError:
            return None

        return command

    def play_notification(self, notification: str) -> None:
        """Play the provided notification using the dialogue manager."""
        self.__pending_notifications.append(notification)

    def process(self) -> None:
        """Process things like pending messages, etc."""
        if self.__is_connected == False:
            return

        # Publish all of the pending notifications.
        while True:
            try:
                notification: str = self.__pending_notifications.popleft()
            except IndexError:
                break

            self.__publish_notification(notification)

    class _UserDataForConnectHandle(Protocol):
        pass

    def __handle_connect(
        self,
        client: paho.mqtt.client.Client,
        userdata: _UserDataForConnectHandle,
        flags: paho.mqtt.client.ConnectFlags | Mapping[str, Any],
        reason_code: paho.mqtt.reasoncodes.ReasonCode
        | paho.mqtt.enums.MQTTErrorCode,
    ) -> None:
        """Handle connecting to the MQTT host."""
        if reason_code != 0:
            self.__logger.warning(
                "Host connection failed with reason code %d.", reason_code
            )
            return

        self.__logger.info("Finished connecting to MQTT host.")
        self.__is_connected = True

        # Register callbacks for the topics.
        self.__client.message_callback_add(
            "hermes/intent/#", self.__handle_intent_message
        )

        # Subscribe all of the topics in one go.
        qos = 0
        subscribe_result, message_id = self.__client.subscribe(
            [("hermes/intent/#", qos)]
        )

        if subscribe_result != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            self.__logger.error("Failed to subscribe to topics.")

    class _UserDataForIntentMessageHandle(Protocol):
        pass

    def __handle_intent_message(
        self,
        client: paho.mqtt.client.Client,
        userdata: _UserDataForIntentMessageHandle,
        message: paho.mqtt.client.MQTTMessage,
    ) -> None:
        """Handle intent messages."""
        payload = message.payload.decode("utf8")

        self.__logger.debug(
            "Received a message on topic '%s': %s",
            message.topic,
            payload,
        )

        # The payload needs to be converted to JSON.
        try:
            payload_json = json.loads(payload)

        except json.JSONDecodeError as exception:
            self.__logger.warning(
                "JSON decode exception raised while handling intent "
                + "message: %s",
                exception,
            )
            return

        command = commands.parse_from_intent(payload_json)

        if command is not None:
            self.__pending_commands.append(command)

    def __publish_notification(self, text: str) -> None:
        """Publish the provided notification to the dialogue manager."""
        payload_json = {
            "init": {"type": "notification", "text": text},
            "siteId": "default",
        }
        payload = json.dumps(payload_json)

        self.__client.publish("hermes/dialogueManager/startSession", payload)

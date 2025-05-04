"""Everything needed to use MQTT."""

import collections
import dataclasses
import json
import logging
import time

import commands
import paho.mqtt.client
import paho.mqtt.enums


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
        self.__pending_commands = collections.deque()
        self.__pending_notifications = collections.deque()
        self.__is_connected = False
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

    def pop_command(self) -> None:
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
                notification = self.__pending_notifications.popleft()
            except IndexError:
                break

            self.__publish_notification(notification)

    def __handle_connect(
        self,
        client: paho.mqtt.client.Client,
        userdata: any,
        flags: paho.mqtt.client.ConnectFlags,
        reason_code: paho.mqtt.reasoncodes.ReasonCode,
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

    def __handle_intent_message(
        self,
        client: paho.mqtt.client.Client,
        userdata: any,
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

        command = self.__parse_intent(payload_json)

        if command is not None:
            self.__pending_commands.append(command)

    def __parse_intent(
        self, intent_json: dict[any]
    ) -> None | commands.StatusCommand | commands.MoveControlCommand:
        """Parse an intent from JSON.

        Return a command if one is recognized.
        """
        # Try to get the intent name.
        try:
            intent = intent_json["intent"]

        except KeyError:
            self.__logger.warning("Invalid intent message received.")
            return None

        try:
            intent_name = intent["intentName"]

        except KeyError:
            self.__logger.warning("Invalid intent message received.")
            return None

        if intent_name == "GetStatus":
            self.__logger.info("Received a get status intent.")
            return commands.StatusCommand()

        elif intent_name == "MovePart":
            self.__logger.info("Received a move control intent.")
            return self.__parse_move_control(intent_json)

        self.__logger.warning("Unrecognized intent '%s'.", intent_name)
        return None

    def __parse_move_control(self, intent_json: dict[any]) -> None:
        """Parse a move control intent from JSON."""
        try:
            slots = intent_json["slots"]

        except KeyError:
            self.__logger.warning(
                "Invalid move control intent: missing slots."
            )
            return None

        # Try to find the control name and direction in the slots.
        control_name = None
        direction = None

        for slot in slots:
            # Each slot must have a name and a value.
            try:
                slot_name = slot["slotName"]

            except KeyError:
                continue

            try:
                slot_value = slot["rawValue"]

            except KeyError:
                continue

            if slot_name == "name":
                control_name = slot_value

            elif slot_name == "direction":
                if slot_value == "raise":
                    direction = "up"

                elif slot_value == "lower":
                    direction = "down"

        if control_name is None:
            self.__logger.warning(
                "Invalid move control intent: missing control name."
            )
            return None

        if direction is None:
            self.__logger.warning(
                "Invalid move control intent: missing direction."
            )
            return None

        self.__logger.info(
            "Recognized move control intent: move '%s' '%s'.",
            control_name,
            direction,
        )
        return commands.MoveControlCommand(control_name, direction)

    def __publish_notification(self, text: str) -> None:
        """Publish the provided notification to the dialogue manager."""
        payload_json = {
            "init": {"type": "notification", "text": text},
            "siteId": "default",
        }
        payload = json.dumps(payload_json)

        self.__client.publish("hermes/dialogueManager/startSession", payload)

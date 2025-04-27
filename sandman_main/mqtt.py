"""Everything needed to use MQTT."""

import collections
import json
import logging
import time

import commands
import paho.mqtt.client
import paho.mqtt.enums


class MQTTClient:
    """Functionality to communicate with an MQTT broker."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.mqtt_client")
        self.__pending_commands = collections.deque()
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
                self.__logger.info("Connected to MQTT host.")
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

    def pop_command(self) -> None:
        """Pop the next pending command off the queue, if there is one.

        Returns the command or None if the queue is empty.
        """
        try:
            command = self.__pending_commands.popleft()
        except IndexError:
            return None

        return command

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

        # Try to get the intent name.
        try:
            intent = payload_json["intent"]

        except KeyError:
            self.__logger.warning("Invalid intent message received.")
            return

        try:
            intent_name = intent["intentName"]

        except KeyError:
            self.__logger.warning("Invalid intent message received.")
            return

        if intent_name == "GetStatus":
            self.__logger.info("Received a get status intent.")
            self.__pending_commands.append(commands.StatusCommand())

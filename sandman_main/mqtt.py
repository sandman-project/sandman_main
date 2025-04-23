"""Everything needed to use MQTT."""

import logging
import time

import paho.mqtt.client
import paho.mqtt.enums


class MQTTClient:
    """Functionality to communicate with an MQTT broker."""

    def __init__(self) -> None:
        """Initialize the instance."""
        self.__logger = logging.getLogger("sandman.mqtt_client")
        pass

    def connect(self) -> bool:
        """Connect to the broker."""
        self.__client = paho.mqtt.client.Client()

        self.__client.on_connect = self.handle_connect

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

    def handle_connect(
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
            "hermes/intent/#", self.handle_intent_message
        )

        # Subscribe all of the topics in one go.
        qos = 0
        subscribe_result, message_id = self.__client.subscribe(
            [("hermes/intent/#", qos)]
        )

        if subscribe_result != paho.mqtt.enums.MQTTErrorCode.MQTT_ERR_SUCCESS:
            self.__logger.error("Failed to subscribe to topics.")

    def handle_intent_message(
        self,
        client: paho.mqtt.client.Client,
        userdata: any,
        message: paho.mqtt.client.MQTTMessage,
    ) -> None:
        """Handle intent messages."""
        self.__logger.debug(
            "Received a message on topic '%s': %s",
            message.topic,
            message.payload.decode(),
        )

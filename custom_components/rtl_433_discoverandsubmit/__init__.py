"""Home Assistant integration for rtl_433 device discovery."""

from collections import defaultdict
import logging
import asyncio
try:
    import paho.mqtt.client as mqtt
except Exception:  # pragma: no cover - optional dependency may be missing
    mqtt = None

from .const import DOMAIN, DATA_DEVICES, DATA_PENDING
from .discovery import DiscoveryManager
from .decode import parse_mqtt_message

_LOGGER = logging.getLogger(__name__)

class MQTTListener:
    """Listen to MQTT messages from rtl_433."""

    def __init__(self, config, message_callback):
        self.config = config
        self._callback = message_callback
        self._running = False
        self._client = None
        self._loop = None

    async def start(self):
        """Connect to the MQTT broker and begin listening."""
        if mqtt is None:
            _LOGGER.error("paho-mqtt is required for MQTT listener but not installed")
            return

        self._running = True
        self._loop = asyncio.get_running_loop()
        _LOGGER.debug("MQTT listener starting with config: %s", self.config)

        def on_connect(client, userdata, flags, rc):
            _LOGGER.debug("MQTT connected with result code: %s", rc)
            client.subscribe(self.config.get("topic", "rtl_433/+/events"))

        def on_message(client, userdata, msg):
            if not self._running:
                return
            payload = msg.payload.decode()
            _LOGGER.debug("Received MQTT message on %s: %s", msg.topic, payload)
            device = parse_mqtt_message(msg.topic, payload)
            if device:
                _LOGGER.debug("Parsed device from MQTT message: %s", device)
                asyncio.run_coroutine_threadsafe(
                    self._callback(device), self._loop
                )

        self._client = mqtt.Client()
        username = self.config.get("mqtt_username")
        password = self.config.get("mqtt_password")
        if username or password:
            self._client.username_pw_set(username, password)
        self._client.on_connect = on_connect
        self._client.on_message = on_message

        server = self.config.get("mqtt_server", "localhost")
        port = int(self.config.get("mqtt_port", 1883))
        self._client.connect_async(server, port)
        self._client.loop_start()

    async def stop(self):
        """Stop listening and disconnect from the broker."""
        self._running = False
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
        _LOGGER.debug("MQTT listener stopped")

    async def simulate_message(self, topic, payload):
        """Helper for tests to feed a message."""
        if self._running:
            _LOGGER.debug("Simulating MQTT message on %s: %s", topic, payload)
            device = parse_mqtt_message(topic, payload)
            if device:
                _LOGGER.debug("Parsed device from MQTT message: %s", device)
                await self._callback(device)
            else:
                _LOGGER.debug("Message on %s did not produce a device", topic)

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, defaultdict(dict))
    _LOGGER.debug("Setting up integration domain storage")
    return True

async def async_setup_entry(hass, entry):
    data = hass.data[DOMAIN][entry.entry_id]
    data[DATA_DEVICES] = {}
    data[DATA_PENDING] = {}

    discovery = DiscoveryManager(hass, entry.entry_id)

    async def handle(payload):
        _LOGGER.debug("Handling incoming payload: %s", payload)
        await discovery.handle_message(payload)

    listener = MQTTListener(entry.data, handle)
    data["listener"] = listener
    await listener.start()
    _LOGGER.debug("Listener started for entry %s", entry.entry_id)
    entry.async_on_unload(listener.stop)
    return True

async def async_unload_entry(hass, entry):
    data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if data and "listener" in data:
        await data["listener"].stop()
        _LOGGER.debug("Listener stopped for entry %s", entry.entry_id)
    return True

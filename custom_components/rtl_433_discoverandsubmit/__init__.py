"""Home Assistant integration for rtl_433 device discovery."""

from collections import defaultdict
import logging

from .const import DOMAIN, DATA_DEVICES, DATA_PENDING
from .discovery import DiscoveryManager
from .decode import parse_mqtt_message

_LOGGER = logging.getLogger(__name__)

class MQTTListener:
    """Simple MQTT listener stub."""

    def __init__(self, config, message_callback):
        self.config = config
        self._callback = message_callback
        self._running = False

    async def start(self):
        self._running = True
        _LOGGER.debug("MQTT listener starting with config: %s", self.config)
        # Real implementation would connect to MQTT broker here

    async def stop(self):
        self._running = False
        _LOGGER.debug("MQTT listener stopped")
        # Real implementation would disconnect here

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

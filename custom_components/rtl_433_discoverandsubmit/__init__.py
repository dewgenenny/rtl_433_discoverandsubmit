"""Home Assistant integration for rtl_433 device discovery."""

from collections import defaultdict

from .const import DOMAIN, DATA_DEVICES, DATA_PENDING
from .discovery import DiscoveryManager
from .decoder import parse_message

class MQTTListener:
    """Simple MQTT listener stub."""

    def __init__(self, config, message_callback):
        self.config = config
        self._callback = message_callback
        self._running = False

    async def start(self):
        self._running = True
        # Real implementation would connect to MQTT broker here

    async def stop(self):
        self._running = False
        # Real implementation would disconnect here

    async def simulate_message(self, payload):
        if self._running:
            await self._callback(payload)

async def async_setup(hass, config):
    hass.data.setdefault(DOMAIN, defaultdict(dict))
    return True

async def async_setup_entry(hass, entry):
    data = hass.data[DOMAIN][entry.entry_id]
    data[DATA_DEVICES] = {}
    data[DATA_PENDING] = {}

    discovery = DiscoveryManager(hass, entry.entry_id)

    async def handle(payload):
        device = parse_message(payload)
        await discovery.handle_message(device)

    listener = MQTTListener(entry.data, handle)
    data["listener"] = listener
    await listener.start()
    entry.async_on_unload(listener.stop)
    return True

async def async_unload_entry(hass, entry):
    data = hass.data[DOMAIN].pop(entry.entry_id, None)
    if data and "listener" in data:
        await data["listener"].stop()
    return True

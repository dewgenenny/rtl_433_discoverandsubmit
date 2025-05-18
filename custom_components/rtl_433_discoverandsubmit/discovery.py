"""Device discovery helper for rtl_433 integration."""

import asyncio
import logging
from .const import DOMAIN, DATA_DEVICES, DATA_PENDING

_LOGGER = logging.getLogger(__name__)

class DiscoveryManager:
    """Manage discovered devices and trigger config flows."""

    def __init__(self, hass, entry_id):
        self.hass = hass
        self.entry_id = entry_id
        self.known = hass.data[DOMAIN][entry_id][DATA_DEVICES]
        self.pending = hass.data[DOMAIN][entry_id][DATA_PENDING]

    async def handle_message(self, payload):
        device_id = f"{payload.get('model')}_{payload.get('id', 'unknown')}"
        _LOGGER.debug("Received payload for device %s: %s", device_id, payload)
        if device_id in self.known or device_id in self.pending:
            _LOGGER.debug("Device %s already known or pending", device_id)
            return
        self.pending[device_id] = payload
        _LOGGER.debug("Triggering config flow for %s", device_id)
        await self.hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "device"},
            data={"entry_id": self.entry_id, "device": payload},
        )

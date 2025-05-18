"""Device discovery helper for rtl_433 integration."""

from .const import DOMAIN, DATA_DEVICES, DATA_PENDING

class DiscoveryManager:
    """Manage discovered devices and trigger config flows."""

    def __init__(self, hass, entry_id):
        self.hass = hass
        self.entry_id = entry_id
        self.known = hass.data[DOMAIN][entry_id][DATA_DEVICES]
        self.pending = hass.data[DOMAIN][entry_id][DATA_PENDING]

    async def handle_message(self, payload):
        device_id = f"{payload.get('model')}_{payload.get('id', 'unknown')}"
        if device_id in self.known or device_id in self.pending:
            return
        self.pending[device_id] = payload
        await self.hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "device"},
            data={"entry_id": self.entry_id, "device": payload},
        )

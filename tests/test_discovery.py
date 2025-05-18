import asyncio
import unittest

from custom_components.rtl_433_discoverandsubmit.discovery import DiscoveryManager
from custom_components.rtl_433_discoverandsubmit.const import DOMAIN, DATA_DEVICES, DATA_PENDING

class FakeFlow:
    def __init__(self):
        self.inits = []
    async def async_init(self, domain, context=None, data=None):
        self.inits.append((domain, context, data))
        return True

class FakeConfigEntries:
    def __init__(self):
        self.flow = FakeFlow()

class FakeHass:
    def __init__(self):
        self.config_entries = FakeConfigEntries()
        self.data = {DOMAIN: {"entry": {DATA_DEVICES: {}, DATA_PENDING: {}}}}

class DiscoveryManagerTest(unittest.TestCase):
    def test_new_device_triggers_flow(self):
        hass = FakeHass()
        manager = DiscoveryManager(hass, "entry")
        payload = {"model": "test", "id": 1}
        asyncio.run(manager.handle_message(payload))
        self.assertEqual(len(hass.config_entries.flow.inits), 1)
        domain, context, data = hass.config_entries.flow.inits[0]
        self.assertEqual(domain, DOMAIN)
        self.assertEqual(data["device"], payload)

    def test_duplicate_device_no_flow(self):
        hass = FakeHass()
        manager = DiscoveryManager(hass, "entry")
        payload = {"model": "test", "id": 1}
        asyncio.run(manager.handle_message(payload))
        asyncio.run(manager.handle_message(payload))
        self.assertEqual(len(hass.config_entries.flow.inits), 1)

    def test_device_not_rediscovered_after_add(self):
        hass = FakeHass()
        manager = DiscoveryManager(hass, "entry")
        payload = {"model": "test", "id": 2}
        asyncio.run(manager.handle_message(payload))
        device_id = "test_2"
        # Simulate user accepting the device
        hass.data[DOMAIN]["entry"][DATA_DEVICES][device_id] = payload
        hass.data[DOMAIN]["entry"][DATA_PENDING].pop(device_id, None)
        asyncio.run(manager.handle_message(payload))
        self.assertEqual(len(hass.config_entries.flow.inits), 1)

if __name__ == '__main__':
    unittest.main()

import asyncio
import types
import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Stub out voluptuous module
vol = types.ModuleType('voluptuous')
vol.Schema = lambda x: x
vol.Required = lambda x: x
vol.Optional = lambda x, default=None: x
sys.modules['voluptuous'] = vol

# Stub out homeassistant modules used by config_flow
ha = types.ModuleType('homeassistant')
config_entries = types.ModuleType('config_entries')

class FakeConfigFlow:
    def __init_subclass__(cls, **kwargs):
        # Ignore domain kwarg from ConfigFlow subclassing
        pass
    def __init__(self):
        self.context = {}
        self.hass = None
    def async_show_form(self, step_id, data_schema=None, description_placeholders=None):
        return {'type': 'form', 'step_id': step_id}
    def async_create_entry(self, title, data):
        return {'type': 'create_entry', 'title': title, 'data': data}

class FakeOptionsFlow:
    pass

config_entries.ConfigFlow = FakeConfigFlow
config_entries.OptionsFlow = FakeOptionsFlow
ha.config_entries = config_entries

class FakeEntry:
    def __init__(self, entry_id="entry"):
        self.entry_id = entry_id
        self.data = {}
        self.options = {}

class FakeConfigEntriesManager:
    def __init__(self, entry):
        self._entry = entry
    def async_get_entry(self, entry_id):
        return self._entry
    def async_update_entry(self, entry, data=None, options=None):
        if options is not None:
            entry.options = options

core = types.ModuleType('core')
core.callback = lambda func: func
ha.core = core

sys.modules['homeassistant'] = ha
sys.modules['homeassistant.config_entries'] = config_entries
sys.modules['homeassistant.core'] = core

from custom_components.rtl_433_discoverandsubmit.config_flow import Rtl433ConfigFlow
from custom_components.rtl_433_discoverandsubmit.const import (
    DOMAIN,
    DATA_DEVICES,
    DATA_PENDING,
    OPTION_DEVICES,
)

class FakeHass:
    def __init__(self):
        self.data = {DOMAIN: {'entry': {DATA_DEVICES: {}, DATA_PENDING: {}}}}
        self.entry = FakeEntry("entry")
        self.config_entries = FakeConfigEntriesManager(self.entry)

class ConfigFlowTitleTest(unittest.TestCase):
    def test_flow_title_after_device(self):
        flow = Rtl433ConfigFlow()
        FakeConfigFlow.__init__(flow)
        flow.hass = FakeHass()
        discovery = {'entry_id': 'entry', 'device': {'model': 'test', 'id': 1}}
        asyncio.run(flow.async_step_device(discovery))
        self.assertEqual(flow.flow_title, 'test 1')

class ConfigFlowPersistTest(unittest.TestCase):
    def test_confirm_persists_device(self):
        hass = FakeHass()
        flow = Rtl433ConfigFlow()
        FakeConfigFlow.__init__(flow)
        flow.hass = hass
        discovery = {'entry_id': 'entry', 'device': {'model': 'test', 'id': 2}}
        asyncio.run(flow.async_step_device(discovery))
        result = asyncio.run(flow.async_step_confirm(user_input={}))
        devices = hass.entry.options.get(OPTION_DEVICES)
        self.assertIn('test_2', devices)
        self.assertEqual(result['type'], 'create_entry')

if __name__ == '__main__':
    unittest.main()

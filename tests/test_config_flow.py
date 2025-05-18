import asyncio
import types
import sys
import unittest

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

core = types.ModuleType('core')
core.callback = lambda func: func
ha.core = core

sys.modules['homeassistant'] = ha
sys.modules['homeassistant.config_entries'] = config_entries
sys.modules['homeassistant.core'] = core

from custom_components.rtl_433_discoverandsubmit.config_flow import Rtl433ConfigFlow
from custom_components.rtl_433_discoverandsubmit.const import DOMAIN, DATA_DEVICES, DATA_PENDING

class FakeHass:
    def __init__(self):
        self.data = {DOMAIN: {'entry': {DATA_DEVICES: {}, DATA_PENDING: {}}}}

class ConfigFlowTitleTest(unittest.TestCase):
    def test_flow_title_after_device(self):
        flow = Rtl433ConfigFlow()
        FakeConfigFlow.__init__(flow)
        flow.hass = FakeHass()
        discovery = {'entry_id': 'entry', 'device': {'model': 'test', 'id': 1}}
        asyncio.run(flow.async_step_device(discovery))
        self.assertEqual(flow.flow_title, 'test 1')

if __name__ == '__main__':
    unittest.main()

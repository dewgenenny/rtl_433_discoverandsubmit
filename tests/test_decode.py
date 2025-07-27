import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from custom_components.rtl_433_discoverandsubmit.decode import parse_mqtt_message, DEVICE_MAPPINGS

class DecodeMessageTest(unittest.TestCase):
    def test_parse_message_populates_model_and_id(self):
        topic = "rtl_433/devices/Weather/12"
        payload = '{"temperature_C": 23, "humidity": 50}'
        result = parse_mqtt_message(topic, payload)
        self.assertIsNotNone(result)
        self.assertEqual(result['model'], 'Weather')
        self.assertEqual(result['id'], '12')
        self.assertIn('temperature_C', result['sensors'])
        self.assertEqual(result['sensors']['temperature_C'], 23)

    def test_parse_message_ignores_events_suffix(self):
        topic = "rtl_433/some_model/events"
        payload = '{"id": 99, "temperature_C": 20}'
        result = parse_mqtt_message(topic, payload)
        self.assertEqual(result['model'], 'some_model')
        # id should come from payload, not the literal word 'events'
        self.assertEqual(result['id'], 99)

if __name__ == '__main__':
    unittest.main()

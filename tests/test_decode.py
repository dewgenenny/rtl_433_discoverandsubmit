import unittest
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

if __name__ == '__main__':
    unittest.main()

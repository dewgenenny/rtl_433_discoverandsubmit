import unittest

from custom_components.rtl_433_discoverandsubmit.decoder import parse_message


class DecoderTest(unittest.TestCase):
    def test_parse_message_extracts_sensors(self):
        msg = {
            "model": "test",
            "id": 1,
            "temperature_C": 23.5,
            "humidity": 56,
            "extra": "ignore",
        }
        device = parse_message(msg)
        self.assertEqual(device["model"], "test")
        self.assertEqual(device["id"], 1)
        self.assertIn("temperature_C", device)
        self.assertIn("humidity", device)
        self.assertNotIn("extra", device)


if __name__ == "__main__":
    unittest.main()

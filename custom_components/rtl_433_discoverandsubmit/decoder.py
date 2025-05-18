"""Utilities for decoding rtl_433 MQTT messages."""

import json
from .utils import load_device_mappings

DEVICE_MAPPINGS = load_device_mappings()


def parse_message(payload):
    """Parse a mqtt payload into a structured device dictionary."""
    if isinstance(payload, (bytes, str)):
        data = json.loads(payload)
    else:
        data = dict(payload)

    device = {
        "model": data.get("model"),
        "id": data.get("id", "unknown"),
    }

    for key in DEVICE_MAPPINGS:
        if key in data:
            device[key] = data[key]

    return device

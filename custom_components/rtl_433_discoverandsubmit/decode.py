import json
import logging
import pkgutil
from typing import Any, Dict, Optional

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Load device mappings from the package data
try:
    mappings_bytes = pkgutil.get_data('rtl_433_discoverandsubmit', 'config/device_mappings.json')
    DEVICE_MAPPINGS = json.loads(mappings_bytes.decode()) if mappings_bytes else {}
except Exception as err:
    _LOGGER.error("Failed to load device mappings: %s", err)
    DEVICE_MAPPINGS = {}


def parse_mqtt_message(topic: str, payload: str) -> Optional[Dict[str, Any]]:
    """Parse an MQTT message published by rtl_433."""
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        _LOGGER.error("Unable to decode JSON payload: %s", payload)
        return None

    parts = topic.split('/')
    if parts and parts[0] == 'rtl_433':
        if len(parts) >= 4 and parts[1] == 'devices':
            data.setdefault('type', parts[1])
            data.setdefault('model', parts[2])
            data.setdefault('id', parts[3])
        elif len(parts) >= 3:
            data.setdefault('model', parts[1])
            data.setdefault('id', parts[2])

    device = {
        'model': data.get('model'),
        'id': data.get('id'),
        'type': data.get('type'),
        'raw': data,
        'sensors': {k: data[k] for k in DEVICE_MAPPINGS if k in data},
    }
    return device


import json
import os
import logging

_LOGGER = logging.getLogger(__name__)

def load_device_mappings():
    """Load device mappings from the JSON configuration file."""
    # Assuming the config directory is relative to this file
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'config', 'device_mappings.json')
    
    # Try alternate path if not found (development environment vs HA installation)
    if not os.path.exists(file_path):
         file_path = os.path.join(current_dir, '..', 'config', 'device_mappings.json')

    _LOGGER.debug(f"Loading device mappings from: {file_path}")
    
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        _LOGGER.error(f"Device mappings file not found at {file_path}")
        return {}
    except json.JSONDecodeError as e:
        _LOGGER.error(f"Error decoding device mappings JSON: {e}")
        return {}

import json
import os
from importlib import resources
import logging

# Locate device mappings bundled with the Home Assistant integration
device_mappings_path = resources.files('custom_components.rtl_433_discoverandsubmit').joinpath('device_mappings.json')


# Define Configuration Paths (legacy constants kept for backward compatibility)
CLI_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/cli_config.json')
DEVICE_MAPPINGS_PATH = device_mappings_path


def load_device_mappings(file_path=device_mappings_path):
    """
    Load device mappings from a JSON file.

    :param file_path: Path to the JSON file containing the device mappings.
    :return: Loaded device mappings.
    """
    logging.info(f"devicemappings path: {file_path}")
    with open(file_path, "rb") as file:
        return json.load(file)

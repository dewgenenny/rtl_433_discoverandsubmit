import json
import os
import pkg_resources
import logging

config_path = pkg_resources.resource_filename('rtl_433_discoverandsubmit', 'config/cli_config.json')
device_mappings_path = pkg_resources.resource_filename('rtl_433_discoverandsubmit', 'config/device_mappings.json')


# Define Configuration Paths
CLI_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/cli_config.json')
DEVICE_MAPPINGS_PATH = os.path.join(os.path.dirname(__file__), '../config/device_mappings.json')



def load_device_mappings(file_path=device_mappings_path):
    """
    Load device mappings from a JSON file.

    :param file_path: Path to the JSON file containing the device mappings.
    :return: Loaded device mappings.
    """
    logging.info(f"devicemappings path: {file_path}")
    with open(file_path, "rb") as file:
        return json.load(file)

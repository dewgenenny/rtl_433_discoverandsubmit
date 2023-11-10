from pathlib import Path
import json
from rtl_433_discoverandsubmit import config
import logging
log_level = getattr(logging, config.configuration['log_level'])
logging.basicConfig(filename=config.configuration['log_filename'], level=log_level)

logging.info("Right at start of device manager")


def initialize_device_storage():
    """Initialize the directory and file for storing devices."""
    logging.debug("Initialize device storage called")
    home = Path.home()
    app_dir = home / ".rtl_433_discoverandsubmit"
    app_dir.mkdir(parents=True, exist_ok=True)
    device_file = app_dir / "devices.json"
    return device_file

def save_devices_to_file(devices):
    """Save the list of devices to a JSON file."""
    device_file = initialize_device_storage()
    logging.debug("device file = " + str(device_file))
    with open(device_file, 'w') as file:
        json.dump(devices, file)

def load_devices_from_file():
    """Load the list of devices from a JSON file. Return an empty list if the file doesn't exist or is corrupted."""
    logging.info("Load devices from file called")
    print("At start of load devices from file")
    device_file = initialize_device_storage()
    logging.debug("device file has been intialised = " + str(device_file))
    try:
        with open(device_file, 'r') as file:
            print("inside load file, before load")
            logging.debug("Before json load")
            devices = json.load(file)
            print("inside load file, after load")
            logging.debug(f"Loaded {len(devices)} devices from the file.")

            # 0.1.7 adds message count, we need to deal with people that have saved devices from previous versions
            for device in devices:
                if 'message_count' not in device:
                    device['message_count'] = 1  # Default value for existing devices

            return devices
    except FileNotFoundError:
        logging.info("File not found error")
        return []
    except json.JSONDecodeError:
        logging.warning(f"Corrupted JSON data in {device_file}. Returning an empty device list.")
        return []
    except Exception as e:
        logging.error(f"Unexpected error while loading devices: {e}")
        return []




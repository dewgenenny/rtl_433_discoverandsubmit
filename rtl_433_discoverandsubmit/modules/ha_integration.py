import json
from rtl_433_discoverandsubmit.modules.mqtt_client import publish_to_topic
from rtl_433_discoverandsubmit.modules.config_loader import load_device_mappings
from rtl_433_discoverandsubmit import config
import logging
log_level = getattr(logging, config.configuration['log_level'])
logging.basicConfig(filename=config.configuration['log_filename'], level=log_level)


NAMING_KEYS = ["brand", "model", "subtype", "channel", "id"]
DEVICE_MAPPINGS = load_device_mappings()


def sanitize(string):
    """Sanitize a string to be used as a topic component."""
    return string.lower().replace(" ", "_")

def rtl_433_device_topic(data):
    """
    Return rtl_433 device topic to subscribe to for a data element.

    :param data: Device data.
    :return: Formatted topic.
    """
    path_elements = []
    for key in NAMING_KEYS:
        if key in data:
            element = sanitize(str(data[key]))
            path_elements.append(element)
    return '/'.join(path_elements)


def publish_ha_config(client, data, retain=True):
    """
    Publish Home Assistant configuration for a device.

    :param client: MQTT client instance.
    :param data: Device data.
    :param retain: Whether to retain the message on the broker or not.
    """
    # Get model and instance details
    model = data.get("model")
    id= data.get("original_id")
    uid = data.get("id")

    logging.info(f"Model: {model}")
    instance = rtl_433_device_topic(data)
    logging.info(f"Instance: {instance}")
    topicprefix = data.get("topicprefix")

    # Iterate through the mappings and publish configuration for each attribute
    for attribute, mapping in DEVICE_MAPPINGS.items():

        if attribute in data:
            # Construct the topic and payload based on the mapping
            logging.debug("Attribute = " + attribute)
            path = f"homeassistant/{mapping['device_type']}/{uid}_{attribute}_{mapping['object_suffix']}/config"

            logging.debug(f"Path: {path}")
            config = mapping["config"].copy()
            config["name"] = attribute

            #deal with type in state topic
            logging.debug("Type is " + str(data.get("type")))

            if "type" in data and "channel" in data:
                logging.debug("In if statement")
                type = data.get("type")
                config["state_topic"] = f"{topicprefix}/devices/{type}/{model}/{channel}/{id}/{attribute}"

            elif "type" in data:
                logging.debug("In if statement")
                type = data.get("type")
                config["state_topic"] = f"{topicprefix}/devices/{type}/{model}/{id}/{attribute}"

            elif "channel" in data:
                channel = data.get("channel")
                config["state_topic"] = f"{topicprefix}/devices/{model}/{channel}/{id}/{attribute}"

            else:
                config["state_topic"] = f"{topicprefix}/devices/{model}/{id}/{attribute}"


            config["unique_id"] = f"rtl_433_{uid}_{attribute}_{mapping['object_suffix']}"
            config["device"] = {
                "identifiers": instance,
                "name": f"{uid}_{mapping['object_suffix']}",
                "model": model,
                "manufacturer": "rtl_433"
            }
            logging.debug(f"Config: {config}")

            # Publish the configuration
            publish_to_topic(client, path, json.dumps(config), retain=retain)



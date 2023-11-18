import paho.mqtt.client as mqtt
import json
from datetime import datetime
from rtl_433_discoverandsubmit import config
from rtl_433_discoverandsubmit.modules.device_manager import save_devices_to_file
import logging
log_level = getattr(logging, config.configuration['log_level'])
logging.basicConfig(filename=config.configuration['log_filename'], level=log_level)

# List to store detected devices
detected_devices = []


def reset_message_counters():
    global detected_devices
    for device in detected_devices:
        if 'message_count' in device:
            device['message_count'] = 0

def sort_detected_devices():
    global detected_devices
    criteria = config.configuration['current_sort_criteria']
    reverse = True if criteria in ["last_detected_time", "message_count"] else False

    if criteria in ["last_detected_time", "message_count"]:
        detected_devices.sort(key=lambda x: x[criteria], reverse=reverse)
    else:
        detected_devices.sort(key=lambda x: x.get('model', '').lower())

    return detected_devices


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    client.subscribe(config.configuration['topic'])

def on_message(client, userdata, msg):
    global detected_devices
    payload = json.loads(msg.payload.decode())

    # Safely get 'id' from payload or default to 'unknown' (fixes https://github.com/dewgenenny/rtl_433_discoverandsubmit/issues/1)
    device_id_value = payload.get('id', 'unknown')

    topicprefix = "/".join(msg.topic.split("/", 2)[:2])

    # Construct a unique device identifier from model and id
    device_id = f"{payload['model']}_{device_id_value}"

    # Check if the device is already in the detected devices list
    existing_device = next((device for device in detected_devices if device['id'] == device_id), None)

    # If the device is new, add it to the list
    if not existing_device:
        device_data = {
            'first_detected_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_detected_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message_count': 1  # Initialize message count
        }
        device_data.update(payload)  # Add all the payload attributes to the dictionary
        device_data['topicprefix']= topicprefix
        old_id = payload.get('id')
        logging.debug("Old ID = "+ str(old_id))
        device_data['original_id'] = old_id
        device_data['id'] = device_id  # Set the id field after updating from payload
        detected_devices.append(device_data)

        #save new device to file, so that it is remembered on startup
        save_devices_to_file(detected_devices)

    else:
        # Update the last detected time and other attributes for the existing device
        existing_device['last_detected_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        existing_device['message_count'] += 1  # Increment message count

        for key, value in payload.items():
            existing_device[key] = value
        existing_device['id'] = device_id  # Set the id field after updating from payload
    sort_detected_devices()


def connect_mqtt():
    """Connect to MQTT broker and return the client."""
    logging.debug("mqtt server = " + config.configuration['mqtt_server'])
    client = mqtt.Client()
    client.username_pw_set(config.configuration['mqtt_username'], config.configuration['mqtt_password'])
    client.connect(config.configuration['mqtt_server'], config.configuration['mqtt_port'], 60)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()
    return client

def publish_to_topic(client, topic, payload, retain=False):
    """
    Publish a message to a specific MQTT topic.

    :param client: MQTT client instance.
    :param topic: Topic to which the message should be published.
    :param payload: Message payload.
    :param retain: Whether to retain the message on the broker or not.
    """
    client.publish(topic, payload, retain=retain)

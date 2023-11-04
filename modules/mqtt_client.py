import paho.mqtt.client as mqtt
import json
from config_loader import get_mqtt_config
from datetime import datetime

import logging

logging.basicConfig(filename='rtl_433_discoverandsubmit.log',  level=logging.DEBUG)



# MQTT Configuration
mqtt_config = get_mqtt_config()

# List to store detected devices
detected_devices = []


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    client.subscribe(mqtt_config.get("topic", "rtl_433/+/events"))

def on_message(client, userdata, msg):
    global detected_devices
    payload = json.loads(msg.payload.decode())

    topicprefix = "/".join(msg.topic.split("/", 2)[:2])
    logging.debug("Topic Prefix = : " + topicprefix)
    # Construct a unique device identifier from model and id
    device_id = f"{payload['model']}_{payload['id']}"

    # Check if the device is already in the detected devices list
    existing_device = next((device for device in detected_devices if device['id'] == device_id), None)

    # If the device is new, add it to the list
    if not existing_device:
        device_data = {
            'first_detected_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_detected_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        device_data.update(payload)  # Add all the payload attributes to the dictionary
        device_data['topicprefix']= topicprefix
        old_id = payload.get('id')
        logging.debug("Old ID = "+ str(old_id))
        device_data['original_id'] = old_id
        device_data['id'] = device_id  # Set the id field after updating from payload
        detected_devices.append(device_data)

    else:
        # Update the last detected time and other attributes for the existing device
        existing_device['last_detected_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for key, value in payload.items():
            existing_device[key] = value
        existing_device['id'] = device_id  # Set the id field after updating from payload



def connect_mqtt():
    """Connect to MQTT broker and return the client."""
    client = mqtt.Client()
    client.username_pw_set(mqtt_config.get("username"), mqtt_config.get("password"))
    client.connect(mqtt_config.get("server"), mqtt_config.get("port", 1883), 60)
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

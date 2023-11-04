from unicurses import *
from rtl_433_discoverandsubmit.modules.mqtt_client import connect_mqtt, detected_devices
from rtl_433_discoverandsubmit.modules.ha_integration import publish_ha_config
from pprint import pprint
import argparse
from rtl_433_discoverandsubmit import config
import logging


def init_ui():
    """Initialize the Unicurses UI."""
    stdscr = initscr()
    cbreak()
    noecho()
    keypad(stdscr, True)
    timeout(1000)  # Wait for 1 second
    return stdscr


def end_ui():
    """End the Unicurses UI session."""
    endwin()

def display_device_list(stdscr, devices, selected_index):
    """Display the list of detected devices in a table format."""
    y, x = 0, 0
    move(y, x)
    addstr("Device ID".ljust(20) + " | " + "First Detected".ljust(19) + " | " + "Last Detected".ljust(19))
    move(y + 1, x)
    addstr("-" * 20 + "+" + "-" * 21 + "+" + "-" * 21)

    # Display each device entry in the list
    for idx, device in enumerate(devices):
        move(y + idx + 2, x)
        if idx == selected_index:
            attron(A_REVERSE)

        device_str = str(device['id']).ljust(20) + " | " + \
                     str(device['first_detected_time']).ljust(19) + " | " + \
                     str(device['last_detected_time']).ljust(19)
        addstr(device_str)

        if idx == selected_index:
            attroff(A_REVERSE)

        height, width = getmaxyx(stdscr)
        move(height - 2, 0)  # Move to second last line of the screen
        addstr("Choose an entry and hit enter for more details or press q to quit.")


def display_device_details(stdscr, device):
    """Display detailed information about the selected device."""
    y, x = 0, 0
    move(y, x )
    addstr(f"Details for {device.get('model', 'Unknown Model')}:")

    for key, value in device.items():
        y += 1
        move(y + 1, x)
        addstr(f"{key}: {value}")
        height, width = getmaxyx(stdscr)
        move(height - 2, 0)  # Move to second last line of the screen
        addstr("Press a to add to Home Assistant, b to go back to the list")

def main_loop(stdscr):
    """Main UI loop."""
    selected_index = 0
    in_detailed_view = False
    mqtt_client = connect_mqtt()

    while True:
        clear()
        height, width = getmaxyx(stdscr)

        if not in_detailed_view:
            display_device_list(stdscr, detected_devices, selected_index)
        else:
            display_device_details(stdscr, detected_devices[selected_index])

        key = getch()
        if key == KEY_DOWN and not in_detailed_view and selected_index < len(detected_devices) - 1:
            selected_index += 1
        elif key == KEY_UP and not in_detailed_view and selected_index > 0:
            selected_index -= 1
        elif key == ord('q'):
            mqtt_client.disconnect()
            break
        elif key == ord('\n') and not in_detailed_view:
            in_detailed_view = True
        elif key == ord('b') and in_detailed_view:
            in_detailed_view = False
        elif key == ord('a') and in_detailed_view:
            #add_device_to_ha(detected_devices[selected_index])
            pprint(detected_devices[selected_index])
            publish_ha_config(mqtt_client,detected_devices[selected_index])

            move(5, 0)
            addstr("Device added to Home Assistant!")  # Feedback to use)
        elif key == ord('q'):
            mqtt_client.disconnect()
            break
        else:
            move(height - 1, 0)  # Move to the last line of the screen
            clrtoeol()  # Clear the line
            addstr("Invalid keypress. Press 'q' to quit or 'Enter' for device details.")


        #mqtt_client.loop(timeout=0.1)

def main():
    parser = argparse.ArgumentParser(description='rtl_433 to Home Assistant bridge.')

    parser.add_argument('--mqtt_server', required=True, help='MQTT server address (e.g., "192.168.1.10").')
    parser.add_argument('--mqtt_port', type=int, default=1883, help='MQTT server port (default: 1883).')
    parser.add_argument('--mqtt_username', default=None, help='MQTT username (if authentication is required).')
    parser.add_argument('--mqtt_password', default=None, help='MQTT password (if authentication is required).')
    parser.add_argument('--topic', default="rtl_433/+/events", help='Topic to listen to (e.g., "rtl_433/+/events").')

    args = parser.parse_args()

    config.configuration['mqtt_server'] = args.mqtt_server
    config.configuration['mqtt_port'] = args.mqtt_port
    config.configuration['mqtt_username'] = args.mqtt_username
    config.configuration['mqtt_password'] = args.mqtt_password
    config.configuration['topic'] = args.topic


    stdscr = init_ui()
    try:
        main_loop(stdscr)
    finally:
        end_ui()







if __name__ == "__main__":
    main()


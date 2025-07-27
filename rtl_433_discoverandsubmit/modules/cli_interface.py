import curses
from rtl_433_discoverandsubmit.modules.mqtt_client import connect_mqtt, detected_devices, sort_detected_devices
global detected_devices
from rtl_433_discoverandsubmit.modules.ha_integration import publish_ha_config
from  rtl_433_discoverandsubmit.modules.device_manager import load_devices_from_file, save_devices_to_file
from rtl_433_discoverandsubmit.modules.mqtt_client import reset_message_counters

from rtl_433_discoverandsubmit import config
from pprint import pprint
import argparse
import logging
log_level = getattr(logging, config.configuration['log_level'])
logging.basicConfig(filename=config.configuration['log_filename'], level=log_level)






def init_ui():
    """Initialize the curses UI."""
    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(True)
    stdscr.timeout(1000)  # Wait for 1 second
    return stdscr




def end_ui():
    """End the curses UI session."""
    curses.echo()
    curses.nocbreak()
    curses.endwin()

def truncate_string(string, max_length):
    """Truncate a string to a maximum length, adding an ellipsis if truncated."""
    return (string[:max_length-3] + '...') if len(string) > max_length else string


def display_device_list(stdscr, devices, selected_index, scroll_offset):
    """Display the list of detected devices in a table format."""
    # Define column widths
    id_width = 25
    message_count_width = 10
    first_detected_width = 19
    last_detected_width = 19


    height, width = stdscr.getmaxyx()
    y, x = 0, 0

    stdscr.move(y, x)
    stdscr.addstr("Device ID".ljust(id_width) + " | " + "Msg Count".ljust(message_count_width) + " | " + "First Detected".ljust(first_detected_width) + " | " + "Last Detected".ljust(last_detected_width))

    stdscr.move(y + 1, x)
    stdscr.addstr("-" * 20 + "+" + "-" * 11 + "+" + "-" * 21 + "+" + "-" * 21)

    stdscr.move(height - 3, 0)  # Move to the third last line of the screen
    stdscr.addstr("Press 's' to sort by last detected time, model, or message count. Press 'k' to reset counters")


    # Display each device entry in the list
    for idx, device in enumerate(devices[scroll_offset:]):  # Start from the scroll offset
        stdscr.move(y + idx + 2, x)
        if idx == selected_index - scroll_offset:  # Adjusted for scroll_offset
            stdscr.attron(curses.A_REVERSE)


        device_str = f"{truncate_string(device['id'], id_width).ljust(id_width)} | {str(device['message_count']).ljust(message_count_width)} | " + \
                     f"{device['first_detected_time'].ljust(first_detected_width)} | " + \
                     f"{device['last_detected_time'].ljust(last_detected_width)}"
        stdscr.addstr(device_str)

        if idx == selected_index - scroll_offset:  # Adjusted for scroll_offset
            stdscr.attroff(curses.A_REVERSE)


        if y + idx + 2 >= height - 2:  # Check if we've reached the bottom of the screen
            break

    stdscr.move(height - 2, 0)  # Move to second last line of the screen
    stdscr.addstr("Choose an entry and hit enter for more details or press q to quit.")



def display_device_details(stdscr, device):
    """Display detailed information about the selected device."""
    y, x = 0, 0
    stdscr.move(y, x)
    stdscr.addstr(f"Details for {device.get('model', 'Unknown Model')}:")

    for key, value in device.items():
        y += 1
        stdscr.move(y + 1, x)
        stdscr.addstr(f"{key}: {value}")
        height, width = stdscr.getmaxyx()
        stdscr.move(height - 2, 0)  # Move to second last line of the screen
        stdscr.addstr("Press a to add to Home Assistant, b to go back to the list")

def main_loop(stdscr):
    """Main UI loop."""
    global current_sort_criteria
    global detected_devices
    scroll_offset = 0
    selected_index = 0
    in_detailed_view = False
    detailed_device = None
    mqtt_client = connect_mqtt()

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if not in_detailed_view:
            display_device_list(stdscr, detected_devices, selected_index, scroll_offset)
        else:
            display_device_details(stdscr, detailed_device)

        key = stdscr.getch()
        # Check if 'k' is pressed
        if key == ord('k'):
            reset_message_counters()
        if key == ord('s'):
    # Cycle through sorting criteria
            current_criteria = config.configuration['current_sort_criteria']
            if current_criteria == "last_detected_time":
                config.configuration['current_sort_criteria'] = "model"
            elif current_criteria == "model":
                config.configuration['current_sort_criteria'] = "message_count"
            else:
                config.configuration['current_sort_criteria'] = "last_detected_time"
            sort_detected_devices()
            stdscr.refresh()
        if key == curses.KEY_RESIZE:
            # Handle the resizing of the console
            stdscr.clear()  # Clear the screen
            stdscr.refresh()  # Refresh the entire screen

            continue  # Skip the rest of the loop and redraw on the next iteration
        if key == curses.KEY_DOWN and not in_detailed_view:
            if selected_index < len(detected_devices) - 1:
                selected_index += 1
            if selected_index - scroll_offset > height - 4:  # -4 accounts for header and footer lines
                scroll_offset += 1
        elif key == curses.KEY_UP and not in_detailed_view:
            if selected_index > 0:
                selected_index -= 1
            if selected_index < scroll_offset:
                scroll_offset -= 1
        elif key == ord('q'):
            mqtt_client.disconnect()
            save_devices_to_file(detected_devices)
            break
        elif key == ord('\n') and not in_detailed_view:
            detailed_device = detected_devices[selected_index]
            in_detailed_view = True
        elif key == ord('b') and in_detailed_view:
            in_detailed_view = False
            detailed_device = None
        elif key == ord('a') and in_detailed_view:
            publish_ha_config(mqtt_client, detailed_device)

            stdscr.move(5, 0)
            stdscr.addstr("Device added to Home Assistant!")  # Feedback to user
        elif key == ord('q'):
            save_devices_to_file(detected_devices)
            mqtt_client.disconnect()
            break
        else:
            stdscr.move(height - 1, 0)  # Move to the last line of the screen
            stdscr.clrtoeol()  # Clear the line
            stdscr.addstr("Invalid keypress. Press 'q' to quit or 'Enter' for device details.")


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


    try:
        loaded_devices = load_devices_from_file()
        detected_devices.clear()  # Clear the contents of the list
        detected_devices.extend(loaded_devices)  # Extend it with the loaded devices
        logging.debug(f"Loaded devices: {loaded_devices}")

    except Exception as e:
        logging.error(f"Error during device loading: {str(e)}")


    stdscr = init_ui()
    try:
        main_loop(stdscr)
    finally:
        end_ui()







if __name__ == "__main__":
    main()


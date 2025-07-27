# rtl_433_discoverandsubmit

A Home Assistant integration that connects to an MQTT server, listens to `rtl_433` events and allows users to add devices through the standard discovery flow.

[Link to GitHub project](https://github.com/dewgenenny/rtl_433_discoverandsubmit)

## Features
- Connects to an MQTT server.
- Listens to `rtl_433` events in real-time.
- Uses Home Assistant's config flow to manage devices.
- No entities are created without user confirmation.
- Includes a command line interface for manual discovery.
- Allows sorting of devices by last seen time, model or message count.
- Press **k** in the CLI to reset message counters.

[![Upload Python Package](https://github.com/dewgenenny/rtl_433_discoverandsubmit/actions/workflows/python-publish.yml/badge.svg)](https://github.com/dewgenenny/rtl_433_discoverandsubmit/actions/workflows/python-publish.yml)

Screenshot of devices listed

![img_1.png](https://github.com/dewgenenny/rtl_433_discoverandsubmit/raw/main/Screenshots/img_3.png)

Detailed device view and opportunity to add to Home Assistant
![img.png](https://github.com/dewgenenny/rtl_433_discoverandsubmit/raw/main/Screenshots/img1.png)

Device added to Home Assistant
![img_2.png](https://github.com/dewgenenny/rtl_433_discoverandsubmit/raw/main/Screenshots/img_2.png)
## Installation

You can install `rtl_433_discoverandsubmit` directly from PyPI:

```bash
pip install rtl_433_discoverandsubmit
```


## Usage

Install the custom integration and add it via Home Assistant's integrations page. During setup you will be asked for MQTT connection details and the topic to listen to. Newly discovered devices will trigger a prompt asking whether they should be added.

The package also installs a small CLI tool called `rtl_433_discoverandsubmit` which can be used without Home Assistant. Run it with your MQTT connection details:

```bash
rtl_433_discoverandsubmit --mqtt_server 192.168.1.10 --mqtt_port 1883 --topic rtl_433/+/events
```

Use the **s** key to cycle sorting of detected devices and **k** to reset the message counters if you want to start again. Accepted devices are persisted in `~/.rtl_433_discoverandsubmit/devices.json`.

##Contributing

Feedback, bug reports, and pull requests are super welcome on this project. If you face any issues, please raise them in the issue tracker.

##License

This project is licensed under the MIT License. See the LICENSE file for more details.


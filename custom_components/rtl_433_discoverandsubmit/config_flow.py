"""Config flow for rtl_433_discoverandsubmit integration."""

from __future__ import annotations

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN
from .const import DATA_DEVICES, DATA_PENDING, OPTION_DEVICES

_LOGGER = logging.getLogger(__name__)


class Rtl433ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the integration."""

    VERSION = 1

    def __init__(self):
        self._device_data = None

    @property
    def flow_title(self) -> str:  # pragma: no cover - simple property
        """Return the title of the current flow."""
        placeholders = self.context.get("title_placeholders")
        if placeholders:
            model = placeholders.get("model", "rtl_433")
            devid = placeholders.get("id")
            return f"{model} {devid}" if devid is not None else model

        if self._device_data:
            device = self._device_data["device"]
            model = device.get("model", "rtl_433")
            devid = device.get("id")
            return f"{model} {devid}" if devid is not None else model

        return "RTL_433 Discover and Submit"

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            _LOGGER.debug("User provided MQTT settings: %s", user_input)
            return self.async_create_entry(title="rtl_433 MQTT", data=user_input)

        _LOGGER.debug("Showing initial configuration form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("mqtt_server"): str,
                    vol.Optional("mqtt_port", default=1883): int,
                    vol.Optional("mqtt_username"): str,
                    vol.Optional("mqtt_password"): str,
                    vol.Optional("topic", default="rtl_433/+/events"): str,
                }
            ),
        )

    async def async_step_device(self, discovery_info):
        """Handle a newly discovered device."""
        _LOGGER.debug("Device discovered: %s", discovery_info)
        self._device_data = discovery_info
        self.context["title_placeholders"] = {
            "model": discovery_info["device"].get("model", "unknown"),
            "id": discovery_info["device"].get("id", "unknown"),
        }
        return await self.async_step_confirm()

    def _device_title(self) -> str:
        device = self._device_data["device"]
        model = device.get("model", "rtl_433")
        devid = device.get("id")
        return f"{model} {devid}" if devid is not None else model

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            device = self._device_data["device"]
            entry_id = self._device_data["entry_id"]
            device_id = f"{device.get('model')}_{device.get('id', 'unknown')}"
            pending = self.hass.data[DOMAIN][entry_id][DATA_PENDING]
            _LOGGER.debug("User accepted device %s", self._device_data)
            self.hass.data[DOMAIN][entry_id][DATA_DEVICES][device_id] = device
            entry = self.hass.config_entries.async_get_entry(entry_id)
            stored = dict(entry.options.get(OPTION_DEVICES, {}))
            stored[device_id] = device
            self.hass.config_entries.async_update_entry(
                entry,
                options={**entry.options, OPTION_DEVICES: stored},
            )
            pending.pop(device_id, None)
            return self.async_create_entry(
                title=self._device_title(),
                data=self._device_data,
            )

        device = self._device_data["device"]
        _LOGGER.debug("Asking user to confirm device %s", self._device_data)
        placeholders = {
            "model": device.get("model", "unknown"),
            "id": device.get("id", "unknown"),
            "sensors": ", ".join(device.get("sensors", {}).keys()) or "none",
        }

        return self.async_show_form(
            step_id="confirm",
            description_placeholders=placeholders,
        )

    async def async_step_ignore(self, user_input=None):
        """Ignore a discovered device."""
        device = self._device_data["device"]
        entry_id = self._device_data["entry_id"]
        device_id = f"{device.get('model')}_{device.get('id', 'unknown')}"
        self.hass.data[DOMAIN][entry_id][DATA_PENDING].pop(device_id, None)
        _LOGGER.debug("Device %s ignored by user", self._device_data)
        return self.async_abort(reason="user_declined")


@callback
def async_get_options_flow(config_entry):
    return Rtl433OptionsFlowHandler(config_entry)


class Rtl433OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            _LOGGER.debug("Options updated: %s", user_input)
            return self.async_create_entry(title="", data=user_input)

        _LOGGER.debug("Showing options flow form")
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Optional("topic", default=self.config_entry.options.get("topic", self.config_entry.data.get("topic"))): str}),
        )

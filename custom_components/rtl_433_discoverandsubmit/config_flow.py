"""Config flow for rtl_433_discoverandsubmit integration."""

from __future__ import annotations

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class Rtl433ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the integration."""

    VERSION = 1

    def __init__(self):
        self._device_data = None

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
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        if user_input is not None:
            if user_input.get("use_device"):
                _LOGGER.debug("User accepted device %s", self._device_data)
                return self.async_create_entry(
                    title=self._device_data["device"].get("model", "rtl_433"),
                    data=self._device_data,
                )
            _LOGGER.debug("User declined device %s", self._device_data)
            return self.async_abort(reason="user_declined")
        _LOGGER.debug("Asking user to confirm device %s", self._device_data)
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({vol.Required("use_device", default=True): bool}),
        )


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

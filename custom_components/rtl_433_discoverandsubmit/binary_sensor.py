
"""Binary sensor platform for rtl_433_discoverandsubmit."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN, DATA_DEVICES, OPTION_DEVICES
from .device_mappings_loader import load_device_mappings

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    listener = data["listener"]
    known_devices = data[DATA_DEVICES]
    
    # Load mappings
    mappings = load_device_mappings()
    
    entities = []
    
    # Create sensors for all known devices in the config entry
    for device_id, device_data in known_devices.items():
        original_model = device_data.get("model")
        
        # Iterate over all possible attributes in the device data that match our mappings
        for key, value in device_data.items():
             if key in mappings and mappings[key]["device_type"] == "binary_sensor":
                 mapping = mappings[key]
                 entities.append(
                     Rtl433BinarySensor(
                         listener, 
                         device_id, 
                         device_data, 
                         key, 
                         mapping
                     )
                 )
    
    async_add_entities(entities)

class Rtl433BinarySensor(BinarySensorEntity):
    """Representation of an rtl_433 binary sensor."""

    def __init__(self, listener, device_id, device_data, attribute, mapping):
        """Initialize the sensor."""
        self._listener = listener
        self._device_id = device_id
        self._attribute = attribute
        self._mapping = mapping
        
        # Extract ID components
        self._model = device_data.get("model")
        self._id = device_data.get("id")
        self._original_id = device_data.get("original_id")
        
        # Config
        config = mapping["config"]
        suffix = mapping["object_suffix"]
        
        self._attr_name = f"{self._model} {self._id} {config.get('name', attribute)}"
        self._attr_unique_id = f"rtl_433_{self._device_id}_{attribute}_{suffix}"
        self._attr_device_class = config.get("device_class")
        self._attr_entity_category = config.get("entity_category")
        self._attr_force_update = config.get("force_update", False)
        
        # Payload on/off config
        self._payload_on = config.get("payload_on", "1")
        self._payload_off = config.get("payload_off", "0")
        
        # Device info
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"{self._model} {self._id}",
            "model": self._model,
            "manufacturer": "rtl_433",
            "via_device": (DOMAIN, "rtl_433_host"),
        }
        
        # Set initial state
        self._update_state(device_data.get(attribute))

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""
        self._listener.register_callback(self._handle_message)

    async def _handle_message(self, payload):
        """Handle incoming MQTT message."""
        inc_model = payload.get("model")
        inc_id = payload.get("id")
        
        if inc_model == self._model and str(inc_id) == str(self._id):
            if self._attribute in payload:
                self._update_state(payload[self._attribute])
                self.async_write_ha_state()

    def _update_state(self, value):
        """Update state from raw value."""
        # Check against payload_on configuration
        # Values come in as they are in the JSON json.
        # payload_on in config is usually string "1"
        
        str_val = str(value)
        if str_val == self._payload_on:
            self._attr_is_on = True
        elif str_val == self._payload_off:
            self._attr_is_on = False
        else:
             # Fallback or strict? 
             # If strictly not payload_on, assume off? Or unknown?
             # For now, if it matches neither, keep previous state or None.
             pass

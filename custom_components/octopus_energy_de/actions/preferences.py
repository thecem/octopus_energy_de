"""SmartFlex preference action."""

from __future__ import annotations

from datetime import time

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ..const import DOMAIN

SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): str,
        vol.Required("target_percentage"): vol.All(vol.Coerce(int), vol.Range(min=20, max=100)),
        vol.Required("target_time"): str,
    }
)


def validate_target_time(value: str) -> str:
    """Validate and normalize the target time accepted by Kraken."""
    try:
        parsed = time.fromisoformat(value)
    except ValueError as err:
        raise HomeAssistantError("target_time must use HH:MM or HH:MM:SS") from err
    if not 4 <= parsed.hour <= 17:
        raise HomeAssistantError("target_time must be between 04:00 and 17:59")
    return parsed.strftime("%H:%M")


async def async_set_device_preferences(hass: HomeAssistant, call: ServiceCall) -> None:
    """Set preferences for a discovered SmartFlex device."""
    device_id = call.data["device_id"]
    target_time = validate_target_time(call.data["target_time"])
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = entry.runtime_data
        if runtime and any(
            device.device_id == device_id for device in runtime.smartflex_coordinator.data.devices
        ):
            await runtime.client.set_device_preferences(
                device_id, call.data["target_percentage"], target_time
            )
            await runtime.smartflex_coordinator.async_request_refresh()
            return
    raise HomeAssistantError("SmartFlex device was not found in an active Octopus Energy DE entry")
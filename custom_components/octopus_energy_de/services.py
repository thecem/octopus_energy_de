"""Register Octopus Energy DE services."""

from __future__ import annotations

from functools import partial

from homeassistant.core import HomeAssistant, SupportsResponse

from .actions.consumption import SCHEMA as CONSUMPTION_SERVICE_SCHEMA
from .actions.consumption import async_get_electricity_consumption
from .actions.export import SCHEMA as CONSUMPTION_EXPORT_SERVICE_SCHEMA
from .actions.export import async_export_electricity_consumption_csv
from .actions.preferences import SCHEMA as PREFERENCES_SERVICE_SCHEMA
from .actions.preferences import async_set_device_preferences
from .const import DOMAIN

SERVICE_SET_DEVICE_PREFERENCES = "set_device_preferences"
SERVICE_GET_ELECTRICITY_CONSUMPTION = "get_electricity_consumption"
SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV = "export_electricity_consumption_csv"


def async_register_services(hass: HomeAssistant) -> None:
    if not hass.services.has_service(DOMAIN, SERVICE_SET_DEVICE_PREFERENCES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_DEVICE_PREFERENCES,
            partial(async_set_device_preferences, hass),
            schema=PREFERENCES_SERVICE_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ELECTRICITY_CONSUMPTION,
            partial(async_get_electricity_consumption, hass),
            schema=CONSUMPTION_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV,
            partial(async_export_electricity_consumption_csv, hass),
            schema=CONSUMPTION_EXPORT_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )


def async_unregister_services(hass: HomeAssistant) -> None:
    hass.services.async_remove(DOMAIN, SERVICE_SET_DEVICE_PREFERENCES)
    hass.services.async_remove(DOMAIN, SERVICE_GET_ELECTRICITY_CONSUMPTION)
    hass.services.async_remove(
        DOMAIN, SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV)

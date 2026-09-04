"""Octopus Energy DE integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.client import OctopusEnergyDEClient
from .const import CONF_ACCOUNT_NUMBER, PLATFORMS
from .coordinator import OctopusEnergyDECoordinator


@dataclass
class OctopusEnergyDERuntimeData:
    client: OctopusEnergyDEClient
    coordinator: OctopusEnergyDECoordinator


OctopusEnergyDEConfigEntry = ConfigEntry[OctopusEnergyDERuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: OctopusEnergyDEConfigEntry) -> bool:
    client = OctopusEnergyDEClient(
        async_get_clientsession(hass),
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )
    coordinator = OctopusEnergyDECoordinator(hass, client, entry.data[CONF_ACCOUNT_NUMBER])
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = OctopusEnergyDERuntimeData(client, coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: OctopusEnergyDEConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

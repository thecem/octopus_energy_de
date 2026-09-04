"""Data coordinator for Octopus Energy DE."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.client import OctopusEnergyDEClient
from .api.exceptions import OctopusEnergyDEError
from .api.models.tariff import AccountSnapshot
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN


class OctopusEnergyDECoordinator(DataUpdateCoordinator[AccountSnapshot]):
    def __init__(self, hass: HomeAssistant, client: OctopusEnergyDEClient, account_number: str) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}_{account_number}",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        self.account_number = account_number

    async def _async_update_data(self) -> AccountSnapshot:
        try:
            return await self.client.account_snapshot(self.account_number)
        except OctopusEnergyDEError as err:
            raise UpdateFailed(str(err)) from err

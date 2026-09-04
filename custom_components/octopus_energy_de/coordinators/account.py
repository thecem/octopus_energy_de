"""Base account and tariff coordinator."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..api.client import OctopusEnergyDEClient
from ..api.exceptions import OctopusEnergyDEError
from ..api.models.tariff import AccountSnapshot
from ..const import BASE_SCAN_INTERVAL, DOMAIN


class OctopusEnergyDECoordinator(DataUpdateCoordinator[AccountSnapshot]):
    """Coordinate infrequently changing account and tariff data."""

    def __init__(self, hass: HomeAssistant, client: OctopusEnergyDEClient, account_number: str) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{DOMAIN}_{account_number}",
            update_interval=BASE_SCAN_INTERVAL,
        )
        self.client = client
        self.account_number = account_number

    async def _async_update_data(self) -> AccountSnapshot:
        try:
            return await self.client.account_snapshot(self.account_number)
        except OctopusEnergyDEError as err:
            raise UpdateFailed(str(err)) from err
"""SmartFlex coordinator."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..api.client import OctopusEnergyDEClient
from ..api.exceptions import OctopusEnergyDEError
from ..api.models.smartflex import SmartFlexSnapshot
from ..const import DOMAIN, SMARTFLEX_SCAN_INTERVAL


class OctopusEnergyDESmartFlexCoordinator(DataUpdateCoordinator[SmartFlexSnapshot]):
    """Coordinate frequently changing SmartFlex data."""

    def __init__(self, hass: HomeAssistant, client: OctopusEnergyDEClient, account_number: str) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{DOMAIN}_{account_number}_smartflex",
            update_interval=SMARTFLEX_SCAN_INTERVAL,
        )
        self.client = client
        self.account_number = account_number

    async def _async_update_data(self) -> SmartFlexSnapshot:
        try:
            return await self.client.smartflex_snapshot(self.account_number)
        except OctopusEnergyDEError as err:
            self.logger.debug("SmartFlex data unavailable for account: %s", err)
            return SmartFlexSnapshot()
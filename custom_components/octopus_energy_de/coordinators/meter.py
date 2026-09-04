"""Electricity meter coordinator."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..api.client import OctopusEnergyDEClient
from ..api.exceptions import OctopusEnergyDEError
from ..api.models.tariff import AccountSnapshot
from ..const import DOMAIN, METER_SCAN_INTERVAL
from .account import OctopusEnergyDECoordinator


class OctopusEnergyDEMeterCoordinator(DataUpdateCoordinator[AccountSnapshot]):
    """Coordinate electricity meter data separately from tariffs."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: OctopusEnergyDEClient,
        account_number: str,
        base_coordinator: OctopusEnergyDECoordinator,
    ) -> None:
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{DOMAIN}_{account_number}_meters",
            update_interval=METER_SCAN_INTERVAL,
        )
        self.client = client
        self.account_number = account_number
        self.base_coordinator = base_coordinator

    async def _async_update_data(self) -> AccountSnapshot:
        try:
            return await self.client.meter_snapshot(
                self.account_number, self.base_coordinator.data.electricity
            )
        except OctopusEnergyDEError as err:
            raise UpdateFailed(str(err)) from err

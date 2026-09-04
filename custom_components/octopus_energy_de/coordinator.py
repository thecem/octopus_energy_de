"""Data coordinator for Octopus Energy DE."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.client import OctopusEnergyDEClient
from .api.exceptions import OctopusEnergyDEError
from .api.models.smartflex import SmartFlexSnapshot
from .api.models.tariff import AccountSnapshot
from .const import BASE_SCAN_INTERVAL, DOMAIN, METER_SCAN_INTERVAL, SMARTFLEX_SCAN_INTERVAL


class OctopusEnergyDECoordinator(DataUpdateCoordinator[AccountSnapshot]):
    def __init__(self, hass: HomeAssistant, client: OctopusEnergyDEClient, account_number: str) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
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


class OctopusEnergyDEMeterCoordinator(DataUpdateCoordinator[AccountSnapshot]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: OctopusEnergyDEClient,
        account_number: str,
        base_coordinator: OctopusEnergyDECoordinator,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
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


class OctopusEnergyDESmartFlexCoordinator(DataUpdateCoordinator[SmartFlexSnapshot]):
    def __init__(self, hass: HomeAssistant, client: OctopusEnergyDEClient, account_number: str) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"{DOMAIN}_{account_number}_smartflex",
            update_interval=SMARTFLEX_SCAN_INTERVAL,
        )
        self.client = client
        self.account_number = account_number

    async def _async_update_data(self) -> SmartFlexSnapshot:
        try:
            return await self.client.smartflex_snapshot(self.account_number)
        except OctopusEnergyDEError as err:
            self.logger.debug(
                "SmartFlex data unavailable for account: %s", err)
            return SmartFlexSnapshot()

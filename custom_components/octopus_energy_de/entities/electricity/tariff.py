"""Electricity tariff entities."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from ...api.models.tariff import ElectricitySupply
from ...const import DOMAIN
from ...coordinators.account import OctopusEnergyDECoordinator
from ...tariffs.registry import TariffService

RATE_UNIT = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"


class OctopusTariffEntity(CoordinatorEntity[OctopusEnergyDECoordinator], SensorEntity):
    """Base entity for one normalized electricity supply."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: OctopusEnergyDECoordinator, supply: ElectricitySupply, index: int
    ) -> None:
        super().__init__(coordinator)
        self._supply_id = supply.supply_point_id
        self._index = index
        self._account = coordinator.account_number

    @property
    def _supply(self) -> ElectricitySupply | None:
        return next(
            (
                supply
                for supply in self.coordinator.data.electricity
                if supply.supply_point_id == self._supply_id
            ),
            None,
        )

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._account}_{self._supply_id}")},
            name=f"Octopus Energy DE Electricity {self._index + 1}",
            manufacturer="Octopus Energy",
            model="Electricity supply",
        )


class CurrentRateSensor(OctopusTariffEntity):
    _attr_name = "Current rate"
    _attr_native_unit_of_measurement = RATE_UNIT
    _attr_icon = "mdi:currency-eur"

    def __init__(
        self, coordinator: OctopusEnergyDECoordinator, supply: ElectricitySupply, index: int
    ) -> None:
        super().__init__(coordinator, supply, index)
        self._attr_unique_id = f"{self._account}_{self._supply_id}_current_rate"

    @property
    def native_value(self) -> Decimal | None:
        supply = self._supply
        return TariffService.current_rate(supply.tariff, dt_util.now()) if supply else None

    @property
    def extra_state_attributes(self):
        supply = self._supply
        if not supply:
            return None
        return {
            "tariff_code": supply.tariff.code,
            "tariff_name": supply.tariff.name,
            "tariff_type": supply.tariff.tariff_type,
            "tariff_family": supply.tariff.family,
        }


class NextRateSensor(OctopusTariffEntity):
    _attr_name = "Next rate"
    _attr_native_unit_of_measurement = RATE_UNIT
    _attr_icon = "mdi:clock-fast"

    def __init__(
        self, coordinator: OctopusEnergyDECoordinator, supply: ElectricitySupply, index: int
    ) -> None:
        super().__init__(coordinator, supply, index)
        self._attr_unique_id = f"{self._account}_{self._supply_id}_next_rate"

    @property
    def native_value(self) -> Decimal | None:
        supply = self._supply
        return TariffService.next_rate(supply.tariff, dt_util.now()) if supply else None


class TariffInfoSensor(OctopusTariffEntity):
    _attr_name = "Tariff"
    _attr_icon = "mdi:file-document-outline"

    def __init__(
        self, coordinator: OctopusEnergyDECoordinator, supply: ElectricitySupply, index: int
    ) -> None:
        super().__init__(coordinator, supply, index)
        self._attr_unique_id = f"{self._account}_{self._supply_id}_tariff"

    @property
    def native_value(self) -> str | None:
        supply = self._supply
        return supply.tariff.name if supply else None

    @property
    def extra_state_attributes(self):
        supply = self._supply
        if not supply:
            return None
        tariff = supply.tariff
        return {
            "code": tariff.code,
            "technical_type": tariff.tariff_type,
            "family": tariff.family,
            "valid_from": tariff.valid_from.isoformat() if tariff.valid_from else None,
            "valid_to": tariff.valid_to.isoformat() if tariff.valid_to else None,
            "raw_type": tariff.raw_type,
        }

"""Electricity meter-reading entity."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfEnergy
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ...api.models.tariff import ElectricityMeter, ElectricityMeterReading, ElectricitySupply
from ...const import DOMAIN
from ...coordinators.meter import OctopusEnergyDEMeterCoordinator


class LatestElectricityMeterReadingSensor(
    CoordinatorEntity[OctopusEnergyDEMeterCoordinator], SensorEntity
):
    """Expose the newest reading for one meter register."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:meter-electric"
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OctopusEnergyDEMeterCoordinator,
        supply: ElectricitySupply,
        index: int,
        meter: ElectricityMeter,
        register_obis_code: str,
    ) -> None:
        super().__init__(coordinator)
        self._meter = meter
        self._index = index
        self._account = coordinator.account_number
        self._register_obis_code = register_obis_code
        self._attr_name = f"Meter reading {register_obis_code}"
        self._attr_unique_id = (
            f"{self._account}_{meter.meter_id}_{register_obis_code}_meter_reading"
        )

    @property
    def _reading(self) -> ElectricityMeterReading | None:
        return next(
            (
                reading
                for reading in self.coordinator.data.electricity_meter_readings
                if reading.meter_id == self._meter.meter_id
                and reading.register_obis_code == self._register_obis_code
            ),
            None,
        )

    @property
    def native_value(self) -> Decimal | None:
        reading = self._reading
        return reading.value if reading else None

    @property
    def extra_state_attributes(self) -> dict[str, str | None] | None:
        reading = self._reading
        if not reading:
            return None
        return {
            "meter_number": self._meter.number,
            "meter_type": self._meter.meter_type,
            "read_at": reading.read_at.isoformat() if reading.read_at else None,
            "register_obis_code": reading.register_obis_code,
            "register_type": reading.register_type,
        }

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._account}_{self._meter.meter_id}")},
            name=f"Octopus Energy DE Electricity Meter {self._meter.number or self._index + 1}",
            manufacturer="Octopus Energy",
            model=self._meter.meter_type or "Electricity meter",
        )

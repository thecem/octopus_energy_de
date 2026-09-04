"""Sensors for Octopus Energy DE."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO, PERCENTAGE, UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .api.models.smartflex import SmartFlexDevice
from .api.models.tariff import ElectricityMeter, ElectricityMeterReading, ElectricitySupply
from .const import DOMAIN
from .coordinator import OctopusEnergyDECoordinator
from .tariffs.registry import TariffService

RATE_UNIT = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    runtime = entry.runtime_data
    coordinator: OctopusEnergyDECoordinator = runtime.coordinator
    entities: list[SensorEntity] = []
    for index, supply in enumerate(coordinator.data.electricity):
        entities.extend(
            [
                CurrentRateSensor(coordinator, supply, index),
                NextRateSensor(coordinator, supply, index),
                TariffInfoSensor(coordinator, supply, index),
            ]
        )
        entities.extend(
            LatestElectricityMeterReadingSensor(
                coordinator, supply, index, meter, reading.register_obis_code
            )
            for meter in supply.meters
            for reading in coordinator.data.electricity_meter_readings
            if reading.meter_id == meter.meter_id and reading.register_obis_code
        )
        if supply.property_id:
            entities.append(PreviousDayConsumptionSensor(
                coordinator, supply, index))
    entities.extend(
        SmartFlexDeviceStateSensor(coordinator, device)
        for device in coordinator.data.smartflex.devices
    )
    entities.extend(
        SmartFlexDeviceSocSensor(coordinator, device)
        for device in coordinator.data.smartflex.devices
        if device.state_of_charge is not None
    )
    entities.extend(
        SmartFlexDevicePowerSensor(coordinator, device)
        for device in coordinator.data.smartflex.devices
        if device.active_power_kw is not None
    )
    if coordinator.data.smartflex.dispatches:
        entities.append(SmartFlexDispatchesSensor(coordinator))
    entities.extend(
        SmartFlexChargingSessionsSensor(coordinator, device)
        for device in coordinator.data.smartflex.devices
        if any(session.device_id == device.device_id for session in coordinator.data.smartflex.charging_sessions)
    )
    async_add_entities(entities)


class OctopusTariffEntity(CoordinatorEntity[OctopusEnergyDECoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, supply: ElectricitySupply, index: int) -> None:
        super().__init__(coordinator)
        self._supply_id = supply.supply_point_id
        self._index = index
        self._account = coordinator.account_number

    @property
    def _supply(self) -> ElectricitySupply | None:
        for supply in self.coordinator.data.electricity:
            if supply.supply_point_id == self._supply_id:
                return supply
        return None

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

    def __init__(self, coordinator, supply, index) -> None:
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

    def __init__(self, coordinator, supply, index) -> None:
        super().__init__(coordinator, supply, index)
        self._attr_unique_id = f"{self._account}_{self._supply_id}_next_rate"

    @property
    def native_value(self) -> Decimal | None:
        supply = self._supply
        return TariffService.next_rate(supply.tariff, dt_util.now()) if supply else None


class TariffInfoSensor(OctopusTariffEntity):
    _attr_name = "Tariff"
    _attr_icon = "mdi:file-document-outline"

    def __init__(self, coordinator, supply, index) -> None:
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


class LatestElectricityMeterReadingSensor(OctopusTariffEntity):
    _attr_name = "Latest meter reading"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:meter-electric"

    def __init__(
        self,
        coordinator: OctopusEnergyDECoordinator,
        supply: ElectricitySupply,
        index: int,
        meter: ElectricityMeter,
        register_obis_code: str,
    ) -> None:
        super().__init__(coordinator, supply, index)
        self._meter = meter
        self._register_obis_code = register_obis_code
        self._attr_name = f"Meter reading {register_obis_code}"
        self._attr_unique_id = f"{self._account}_{meter.meter_id}_{register_obis_code}_meter_reading"

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


class PreviousDayConsumptionSensor(OctopusTariffEntity):
    _attr_name = "Previous day consumption"
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL
    _attr_icon = "mdi:flash-outline"

    def __init__(
        self, coordinator: OctopusEnergyDECoordinator, supply: ElectricitySupply, index: int
    ) -> None:
        super().__init__(coordinator, supply, index)
        self._property_id = supply.property_id
        self._attr_unique_id = f"{self._account}_{self._supply_id}_previous_day_consumption"

    @property
    def _consumption(self):
        return next(
            (
                consumption
                for consumption in self.coordinator.data.electricity_consumption
                if consumption.property_id == self._property_id
            ),
            None,
        )

    @property
    def native_value(self) -> Decimal | None:
        consumption = self._consumption
        if not consumption or not consumption.intervals:
            return None
        return sum((interval.value for interval in consumption.intervals), Decimal("0"))

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        consumption = self._consumption
        if not consumption:
            return None
        return {
            "date": consumption.date.isoformat(),
            "intervals": [
                {
                    "start": interval.start.isoformat(),
                    "end": interval.end.isoformat(),
                    "consumption": str(interval.value),
                    "unit": interval.unit,
                }
                for interval in consumption.intervals
            ],
        }


class SmartFlexDeviceEntity(CoordinatorEntity[OctopusEnergyDECoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OctopusEnergyDECoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator)
        self._device_id = device.device_id
        self._account = coordinator.account_number

    @property
    def _device(self) -> SmartFlexDevice | None:
        return next(
            (device for device in self.coordinator.data.smartflex.devices if device.device_id == self._device_id),
            None,
        )

    @property
    def device_info(self) -> DeviceInfo:
        device = self._device
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._account}_{self._device_id}")},
            name=device.name if device else "Octopus Energy DE SmartFlex device",
            manufacturer=device.provider if device and device.provider else "Octopus Energy",
            model=device.device_type if device else "SmartFlex device",
        )


class SmartFlexDeviceStateSensor(SmartFlexDeviceEntity):
    _attr_name = "SmartFlex state"
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: OctopusEnergyDECoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_smartflex_state"

    @property
    def native_value(self) -> str | None:
        device = self._device
        return device.state if device else None

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:
        device = self._device
        if not device:
            return None
        return {"device_type": device.device_type, "smart_control_suspended": device.is_suspended}


class SmartFlexDeviceSocSensor(SmartFlexDeviceEntity):
    _attr_name = "State of charge"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:battery"

    def __init__(self, coordinator: OctopusEnergyDECoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_state_of_charge"

    @property
    def native_value(self) -> Decimal | None:
        device = self._device
        return device.state_of_charge if device else None


class SmartFlexDevicePowerSensor(SmartFlexDeviceEntity):
    _attr_name = "Charging power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_icon = "mdi:lightning-bolt"

    def __init__(self, coordinator: OctopusEnergyDECoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_charging_power"

    @property
    def native_value(self) -> Decimal | None:
        device = self._device
        return device.active_power_kw if device else None


class SmartFlexDispatchesSensor(CoordinatorEntity[OctopusEnergyDECoordinator], SensorEntity):
    _attr_name = "SmartFlex dispatches"
    _attr_icon = "mdi:calendar-clock"
    _attr_has_entity_name = True

    def __init__(self, coordinator: OctopusEnergyDECoordinator) -> None:
        super().__init__(coordinator)
        self._account = coordinator.account_number
        self._attr_unique_id = f"{self._account}_smartflex_dispatches"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.smartflex.dispatches)

    @property
    def extra_state_attributes(self) -> dict[str, list[dict[str, str | None]]]:
        return {
            "dispatches": [
                {
                    "start": dispatch.start.isoformat(),
                    "end": dispatch.end.isoformat(),
                    "energy_kwh": str(dispatch.energy_kwh) if dispatch.energy_kwh is not None else None,
                }
                for dispatch in self.coordinator.data.smartflex.dispatches
            ]
        }


class SmartFlexChargingSessionsSensor(SmartFlexDeviceEntity):
    _attr_name = "SmartFlex charging sessions"
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: OctopusEnergyDECoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_smartflex_charging_sessions"

    @property
    def _sessions(self):
        return tuple(
            session
            for session in self.coordinator.data.smartflex.charging_sessions
            if session.device_id == self._device_id
        )

    @property
    def native_value(self) -> int:
        return len(self._sessions)

    @property
    def extra_state_attributes(self) -> dict[str, list[dict[str, str | None]]]:
        return {
            "sessions": [
                {
                    "start": session.start.isoformat(),
                    "end": session.end.isoformat() if session.end else None,
                    "energy_kwh": str(session.energy_kwh) if session.energy_kwh is not None else None,
                    "cost_eur": str(session.cost_eur) if session.cost_eur is not None else None,
                    "type": session.session_type,
                }
                for session in self._sessions
            ]
        }

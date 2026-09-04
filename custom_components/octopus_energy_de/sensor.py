"""Register Octopus Energy DE sensor entities."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .entities.electricity.meter_reading import LatestElectricityMeterReadingSensor
from .entities.electricity.tariff import CurrentRateSensor, NextRateSensor, TariffInfoSensor
from .entities.smartflex import (
    SmartFlexChargingSessionsSensor,
    SmartFlexDevicePowerSensor,
    SmartFlexDeviceSocSensor,
    SmartFlexDeviceStateSensor,
    SmartFlexDispatchesSensor,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up entities from normalized coordinator data."""
    runtime = entry.runtime_data
    entities: list[SensorEntity] = []
    for index, supply in enumerate(runtime.coordinator.data.electricity):
        entities.extend(
            [
                CurrentRateSensor(runtime.coordinator, supply, index),
                NextRateSensor(runtime.coordinator, supply, index),
                TariffInfoSensor(runtime.coordinator, supply, index),
            ]
        )
        entities.extend(
            LatestElectricityMeterReadingSensor(
                runtime.meter_coordinator, supply, index, meter, reading.register_obis_code
            )
            for meter in supply.meters
            for reading in runtime.meter_coordinator.data.electricity_meter_readings
            if reading.meter_id == meter.meter_id and reading.register_obis_code
        )

    smartflex = runtime.smartflex_coordinator.data
    entities.extend(
        SmartFlexDeviceStateSensor(runtime.smartflex_coordinator, device)
        for device in smartflex.devices
    )
    entities.extend(
        SmartFlexDeviceSocSensor(runtime.smartflex_coordinator, device)
        for device in smartflex.devices
        if device.state_of_charge is not None
    )
    entities.extend(
        SmartFlexDevicePowerSensor(runtime.smartflex_coordinator, device)
        for device in smartflex.devices
        if device.active_power_kw is not None
    )
    if smartflex.dispatches:
        entities.append(SmartFlexDispatchesSensor(
            runtime.smartflex_coordinator))
    entities.extend(
        SmartFlexChargingSessionsSensor(runtime.smartflex_coordinator, device)
        for device in smartflex.devices
        if any(session.device_id == device.device_id for session in smartflex.charging_sessions)
    )
    async_add_entities(entities)

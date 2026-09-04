"""Read-only SmartFlex entities."""

from __future__ import annotations

from decimal import Decimal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..api.models.smartflex import SmartFlexDevice
from ..const import DOMAIN
from ..coordinators.smartflex import OctopusEnergyDESmartFlexCoordinator


class SmartFlexDeviceEntity(CoordinatorEntity[OctopusEnergyDESmartFlexCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator)
        self._device_id = device.device_id
        self._account = coordinator.account_number

    @property
    def _device(self) -> SmartFlexDevice | None:
        return next(
            (device for device in self.coordinator.data.devices if device.device_id == self._device_id),
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

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice) -> None:
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

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice) -> None:
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

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_charging_power"

    @property
    def native_value(self) -> Decimal | None:
        device = self._device
        return device.active_power_kw if device else None


class SmartFlexDispatchesSensor(CoordinatorEntity[OctopusEnergyDESmartFlexCoordinator], SensorEntity):
    _attr_name = "SmartFlex dispatches"
    _attr_icon = "mdi:calendar-clock"
    _attr_has_entity_name = True

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator) -> None:
        super().__init__(coordinator)
        self._account = coordinator.account_number
        self._attr_unique_id = f"{self._account}_smartflex_dispatches"

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data.dispatches)

    @property
    def extra_state_attributes(self) -> dict[str, list[dict[str, str | None]]]:
        return {
            "dispatches": [
                {
                    "start": dispatch.start.isoformat(),
                    "end": dispatch.end.isoformat(),
                    "energy_kwh": str(dispatch.energy_kwh) if dispatch.energy_kwh is not None else None,
                }
                for dispatch in self.coordinator.data.dispatches
            ]
        }


class SmartFlexChargingSessionsSensor(SmartFlexDeviceEntity):
    _attr_name = "SmartFlex charging sessions"
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_smartflex_charging_sessions"

    @property
    def _sessions(self):
        return tuple(session for session in self.coordinator.data.charging_sessions if session.device_id == self._device_id)

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
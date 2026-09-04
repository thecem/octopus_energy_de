"""SmartFlex control switches."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api.models.smartflex import SmartFlexDevice
from .coordinator import OctopusEnergyDESmartFlexCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: OctopusEnergyDESmartFlexCoordinator = entry.runtime_data.smartflex_coordinator
    switches: list[SwitchEntity] = []
    for device in coordinator.data.devices:
        if device.is_suspended is not None:
            switches.append(SmartControlSwitch(coordinator, device))
        switches.append(BoostChargeSwitch(coordinator, device))
    async_add_entities(switches)


class SmartFlexControlSwitch(CoordinatorEntity[OctopusEnergyDESmartFlexCoordinator], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device.device_id
        self._account = coordinator.account_number

    @property
    def _device(self) -> SmartFlexDevice | None:
        return next(
            (
                device
                for device in self.coordinator.data.devices
                if device.device_id == self._device_id
            ),
            None,
        )

    async def _refresh_after_change(self) -> None:
        await self.coordinator.async_request_refresh()


class SmartControlSwitch(SmartFlexControlSwitch):
    _attr_name = "Smart Control"
    _attr_icon = "mdi:car-connected"

    def __init__(
        self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice
    ) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_smart_control"

    @property
    def is_on(self) -> bool:
        device = self._device
        return bool(device and device.is_suspended is False)

    async def async_turn_on(self, **kwargs: object) -> None:
        try:
            await self.coordinator.client.set_smart_control(self._device_id, enabled=True)
            await self._refresh_after_change()
        except Exception as err:
            raise HomeAssistantError(f"Unable to enable Smart Control: {err}") from err

    async def async_turn_off(self, **kwargs: object) -> None:
        try:
            await self.coordinator.client.set_smart_control(self._device_id, enabled=False)
            await self._refresh_after_change()
        except Exception as err:
            raise HomeAssistantError(f"Unable to disable Smart Control: {err}") from err


class BoostChargeSwitch(SmartFlexControlSwitch):
    _attr_name = "Boost Charge"
    _attr_icon = "mdi:lightning-bolt"

    def __init__(
        self, coordinator: OctopusEnergyDESmartFlexCoordinator, device: SmartFlexDevice
    ) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{self._account}_{device.device_id}_boost_charge"

    @property
    def is_on(self) -> bool:
        device = self._device
        return bool(device and device.state and "BOOST" in device.state.upper())

    async def async_turn_on(self, **kwargs: object) -> None:
        try:
            await self.coordinator.client.set_boost_charge(self._device_id, enabled=True)
            await self._refresh_after_change()
        except Exception as err:
            raise HomeAssistantError(f"Unable to enable Boost Charge: {err}") from err

    async def async_turn_off(self, **kwargs: object) -> None:
        try:
            await self.coordinator.client.set_boost_charge(self._device_id, enabled=False)
            await self._refresh_after_change()
        except Exception as err:
            raise HomeAssistantError(f"Unable to disable Boost Charge: {err}") from err

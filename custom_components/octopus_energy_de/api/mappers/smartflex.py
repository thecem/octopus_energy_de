"""Map Kraken SmartFlex responses into normalized models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from ..models.smartflex import (
    SmartFlexChargingSession,
    SmartFlexDevice,
    SmartFlexDispatch,
    SmartFlexSnapshot,
)


def _datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def _decimal(value: Any) -> Decimal | None:
    return Decimal(str(value)) if value is not None else None


def map_smartflex_snapshot(response: dict[str, Any]) -> SmartFlexSnapshot:
    data = response.get("data") or {}
    devices: list[SmartFlexDevice] = []
    sessions: list[SmartFlexChargingSession] = []
    for device in data.get("devices") or []:
        status = device.get("status") or {}
        vehicle = device.get("vehicleVariant") or {}
        device_id = device.get("id")
        if not device_id:
            continue
        devices.append(
            SmartFlexDevice(
                device_id=device_id,
                name=device.get("name") or "SmartFlex device",
                device_type=device.get("deviceType") or "UNKNOWN",
                provider=device.get("provider"),
                state=status.get("currentState"),
                is_suspended=status.get("isSuspended"),
                state_of_charge=_decimal((status.get("stateOfCharge") or {}).get("value")),
                active_power_kw=_decimal((status.get("activePower") or {}).get("value")),
                battery_size_kwh=_decimal(vehicle.get("batterySize")),
            )
        )
        for edge in (device.get("chargingSessions") or {}).get("edges") or []:
            node = edge.get("node") or {}
            start = _datetime(node.get("start"))
            if start:
                sessions.append(
                    SmartFlexChargingSession(
                        device_id=device_id,
                        start=start,
                        end=_datetime(node.get("end")),
                        energy_kwh=_decimal((node.get("energyAdded") or {}).get("value")),
                        cost_eur=_decimal((node.get("cost") or {}).get("amount")),
                        session_type=node.get("type"),
                    )
                )
    dispatches = tuple(
        SmartFlexDispatch(start=start, end=end, energy_kwh=_decimal(item.get("deltaKwh")))
        for item in data.get("completedDispatches") or []
        if (start := _datetime(item.get("startDt") or item.get("start")))
        and (end := _datetime(item.get("endDt") or item.get("end")))
    )
    return SmartFlexSnapshot(
        devices=tuple(devices), dispatches=dispatches, charging_sessions=tuple(sessions)
    )

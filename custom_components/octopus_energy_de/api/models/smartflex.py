"""Normalized SmartFlex models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class SmartFlexDevice:
    """A vehicle or charge point connected to Octopus SmartFlex."""

    device_id: str
    name: str
    device_type: str
    provider: str | None = None
    state: str | None = None
    is_suspended: bool | None = None
    state_of_charge: Decimal | None = None
    active_power_kw: Decimal | None = None
    battery_size_kwh: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SmartFlexDispatch:
    """A completed SmartFlex dispatch window."""

    start: datetime
    end: datetime
    energy_kwh: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SmartFlexChargingSession:
    """A SmartFlex charging session for one device."""

    device_id: str
    start: datetime
    end: datetime | None = None
    energy_kwh: Decimal | None = None
    cost_eur: Decimal | None = None
    session_type: str | None = None


@dataclass(frozen=True, slots=True)
class SmartFlexSnapshot:
    """Read-only SmartFlex data available for an account."""

    devices: tuple[SmartFlexDevice, ...] = field(default_factory=tuple)
    dispatches: tuple[SmartFlexDispatch, ...] = field(default_factory=tuple)
    charging_sessions: tuple[SmartFlexChargingSession, ...] = field(
        default_factory=tuple)

"""Normalized tariff model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from ...tariffs.types import TariffFamily, TariffType
from .rate import IntervalRate, TimeOfUseRate


@dataclass(frozen=True, slots=True)
class Tariff:
    code: str
    name: str
    tariff_type: TariffType
    family: TariffFamily = TariffFamily.UNKNOWN
    description: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    fixed_rate_eur_per_kwh: Decimal | None = None
    interval_rates: tuple[IntervalRate, ...] = field(default_factory=tuple)
    tou_rates: tuple[TimeOfUseRate, ...] = field(default_factory=tuple)
    raw_type: str | None = None


@dataclass(frozen=True, slots=True)
class ElectricityMeter:
    """An electricity meter attached to a supply point."""

    meter_id: str
    number: str | None = None
    meter_type: str | None = None


@dataclass(frozen=True, slots=True)
class ElectricityMeterReading:
    """The most recent reading reported for an electricity meter."""

    meter_id: str
    value: Decimal
    read_at: datetime | None = None
    register_obis_code: str | None = None
    register_type: str | None = None


@dataclass(frozen=True, slots=True)
class ElectricityConsumptionInterval:
    """An electricity consumption interval returned by Kraken."""

    start: datetime
    end: datetime
    value: Decimal
    unit: str


@dataclass(frozen=True, slots=True)
class ElectricityConsumption:
    """Electricity consumption for one property and calendar day."""

    property_id: str
    date: date
    intervals: tuple[ElectricityConsumptionInterval, ...]


@dataclass(frozen=True, slots=True)
class ElectricitySupply:
    supply_point_id: str
    tariff: Tariff
    meters: tuple[ElectricityMeter, ...] = field(default_factory=tuple)
    property_id: str | None = None


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    account_number: str
    electricity: tuple[ElectricitySupply, ...]
    electricity_meter_readings: tuple[ElectricityMeterReading, ...] = field(
        default_factory=tuple)
    electricity_consumption: tuple[ElectricityConsumption, ...] = field(
        default_factory=tuple)

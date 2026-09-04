"""Normalized tariff model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
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
class ElectricitySupply:
    supply_point_id: str
    tariff: Tariff


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    account_number: str
    electricity: tuple[ElectricitySupply, ...]

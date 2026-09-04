"""Normalized rate models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class IntervalRate:
    """A rate with an explicit absolute interval."""

    value_eur_per_kwh: Decimal
    valid_from: datetime
    valid_to: datetime
    name: str | None = None

    def contains(self, moment: datetime) -> bool:
        return self.valid_from <= moment < self.valid_to


@dataclass(frozen=True, slots=True)
class TimeOfUseRate:
    """A recurring local-time rate window."""

    value_eur_per_kwh: Decimal
    active_from: time
    active_to: time
    name: str | None = None

    def contains_local_time(self, value: time) -> bool:
        if self.active_from == self.active_to:
            return True
        if self.active_from < self.active_to:
            return self.active_from <= value < self.active_to
        return value >= self.active_from or value < self.active_to

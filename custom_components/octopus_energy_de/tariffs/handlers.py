"""Generic tariff handlers."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol

from ..api.models.tariff import Tariff
from .types import TariffType


class TariffHandler(Protocol):
    def current_rate(self, tariff: Tariff, now: datetime) -> Decimal | None: ...
    def next_rate(self, tariff: Tariff, now: datetime) -> Decimal | None: ...


class FixedTariffHandler:
    def current_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        return tariff.fixed_rate_eur_per_kwh

    def next_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        return None


class DynamicTariffHandler:
    def current_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        return next((r.value_eur_per_kwh for r in tariff.interval_rates if r.contains(now)), None)

    def next_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        future = [r for r in tariff.interval_rates if r.valid_from > now]
        return min(future, key=lambda r: r.valid_from).value_eur_per_kwh if future else None


class TimeOfUseTariffHandler:
    def current_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        local_time = now.timetz().replace(tzinfo=None)
        return next(
            (r.value_eur_per_kwh for r in tariff.tou_rates if r.contains_local_time(local_time)),
            None,
        )

    def next_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        if not tariff.tou_rates:
            return None
        local_time = now.timetz().replace(tzinfo=None)
        candidates = sorted(tariff.tou_rates, key=lambda r: r.active_from)
        for rate in candidates:
            if rate.active_from > local_time:
                return rate.value_eur_per_kwh
        return candidates[0].value_eur_per_kwh


class UnknownTariffHandler:
    def current_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        if tariff.interval_rates:
            return DynamicTariffHandler().current_rate(tariff, now)
        return tariff.fixed_rate_eur_per_kwh

    def next_rate(self, tariff: Tariff, now: datetime) -> Decimal | None:
        return DynamicTariffHandler().next_rate(tariff, now) if tariff.interval_rates else None


HANDLERS: dict[TariffType, TariffHandler] = {
    TariffType.FIXED: FixedTariffHandler(),
    TariffType.TIME_OF_USE: TimeOfUseTariffHandler(),
    TariffType.DYNAMIC: DynamicTariffHandler(),
    TariffType.UNKNOWN: UnknownTariffHandler(),
}

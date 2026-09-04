"""Tariff service facade."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from ..api.models.tariff import Tariff
from .handlers import HANDLERS


class TariffService:
    """Expose tariff behavior without product-specific branches."""

    @staticmethod
    def current_rate(tariff: Tariff, now: datetime) -> Decimal | None:
        return HANDLERS[tariff.tariff_type].current_rate(tariff, now)

    @staticmethod
    def next_rate(tariff: Tariff, now: datetime) -> Decimal | None:
        return HANDLERS[tariff.tariff_type].next_rate(tariff, now)

"""Tariff type detection."""

from __future__ import annotations

from dataclasses import dataclass

from .types import TariffType

SIMPLE = "SimpleProductUnitRateInformation"
TOU = "TimeOfUseProductUnitRateInformation"


@dataclass(frozen=True, slots=True)
class ProductDescriptor:
    code: str
    is_time_of_use: bool | None
    unit_rate_typename: str | None
    has_forecast: bool


class TariffDetector:
    @staticmethod
    def detect(product: ProductDescriptor) -> TariffType:
        if product.has_forecast:
            return TariffType.DYNAMIC
        if product.unit_rate_typename == TOU:
            return TariffType.TIME_OF_USE
        if product.unit_rate_typename == SIMPLE:
            return TariffType.FIXED
        if product.is_time_of_use:
            return TariffType.TIME_OF_USE
        return TariffType.UNKNOWN

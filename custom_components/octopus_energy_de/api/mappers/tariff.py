"""Map Kraken GraphQL tariff structures into normalized domain models."""

from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal
from typing import Any

from ...tariffs.detector import ProductDescriptor, TariffDetector
from ...tariffs.families import detect_family
from ...tariffs.types import TariffFamily, TariffType
from ..models.rate import IntervalRate, TimeOfUseRate
from ..models.tariff import Tariff


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Kraken timestamp has no timezone: {value}")
    return parsed


def _parse_time(value: str) -> time:
    return time.fromisoformat(value)


def _cents_to_eur(value: Any) -> Decimal:
    return Decimal(str(value)) / Decimal("100")


def _select_forecast_price(info: dict[str, Any]) -> tuple[Decimal | None, str | None]:
    typename = info.get("__typename")
    if typename == "SimpleProductUnitRateInformation":
        value = info.get("latestGrossUnitRateCentsPerKwh")
        return (_cents_to_eur(value), None) if value is not None else (None, None)
    rates = info.get("rates") or []
    if rates:
        value = rates[0].get("latestGrossUnitRateCentsPerKwh")
        return (
            (_cents_to_eur(value), rates[0].get("timeslotName"))
            if value is not None
            else (None, None)
        )
    return None, None


def map_tariff(agreement: dict[str, Any]) -> Tariff:
    product = agreement.get("product") or {}
    rate_info = agreement.get("unitRateInformation") or {}
    forecast = agreement.get("unitRateForecast") or []
    typename = rate_info.get("__typename")
    descriptor = ProductDescriptor(
        code=product.get("code") or "unknown",
        is_time_of_use=product.get("isTimeOfUse"),
        unit_rate_typename=typename,
        has_forecast=bool(forecast),
    )
    tariff_type = TariffDetector.detect(descriptor)
    family = detect_family(
        product.get("code") or "", product.get("fullName"), product.get("description")
    )
    if tariff_type == TariffType.FIXED and family == TariffFamily.UNKNOWN:
        family = TariffFamily.GENERIC_FIXED

    fixed_rate = None
    interval_rates: list[IntervalRate] = []
    tou_rates: list[TimeOfUseRate] = []

    if tariff_type == TariffType.DYNAMIC:
        for item in forecast:
            price, name = _select_forecast_price(item.get("unitRateInformation") or {})
            valid_from = _parse_datetime(item.get("validFrom"))
            valid_to = _parse_datetime(item.get("validTo"))
            if price is not None and valid_from and valid_to:
                interval_rates.append(IntervalRate(price, valid_from, valid_to, name))

    elif tariff_type == TariffType.TIME_OF_USE:
        for rate in rate_info.get("rates") or []:
            value = rate.get("latestGrossUnitRateCentsPerKwh")
            if value is None:
                continue
            for rule in rate.get("timeslotActivationRules") or []:
                start = rule.get("activeFromTime")
                end = rule.get("activeToTime")
                if start and end:
                    tou_rates.append(
                        TimeOfUseRate(
                            value_eur_per_kwh=_cents_to_eur(value),
                            active_from=_parse_time(start),
                            active_to=_parse_time(end),
                            name=rate.get("timeslotName"),
                        )
                    )

    elif tariff_type == TariffType.FIXED:
        value = rate_info.get("latestGrossUnitRateCentsPerKwh")
        if value is not None:
            fixed_rate = _cents_to_eur(value)

    return Tariff(
        code=product.get("code") or "unknown",
        name=product.get("fullName") or product.get("code") or "Unknown tariff",
        description=product.get("description"),
        tariff_type=tariff_type,
        family=family,
        valid_from=_parse_datetime(agreement.get("validFrom")),
        valid_to=_parse_datetime(agreement.get("validTo")),
        fixed_rate_eur_per_kwh=fixed_rate,
        interval_rates=tuple(sorted(interval_rates, key=lambda rate: rate.valid_from)),
        tou_rates=tuple(tou_rates),
        raw_type=typename,
    )

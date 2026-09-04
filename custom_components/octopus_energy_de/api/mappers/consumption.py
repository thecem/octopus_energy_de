"""Map Kraken electricity consumption intervals into normalized models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..models.tariff import ElectricityConsumption, ElectricityConsumptionInterval


def map_electricity_consumption(
    property_id: str, measurement_date: date, response: dict[str, Any]
) -> ElectricityConsumption:
    measurements = (
        ((response.get("data") or {}).get("account") or {}).get("property") or {}
    ).get("measurements") or {}
    intervals = tuple(
        ElectricityConsumptionInterval(
            start=datetime.fromisoformat(
                node["startAt"].replace("Z", "+00:00")),
            end=datetime.fromisoformat(node["endAt"].replace("Z", "+00:00")),
            value=Decimal(str(node["value"])),
            unit=node["unit"],
        )
        for edge in measurements.get("edges") or []
        if (node := edge.get("node"))
        and node.get("startAt")
        and node.get("endAt")
        and node.get("value") is not None
        and node.get("unit")
    )
    return ElectricityConsumption(
        property_id=property_id,
        date=measurement_date,
        intervals=intervals,
    )

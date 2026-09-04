"""Map Kraken electricity meter readings into normalized models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from ..models.tariff import ElectricityMeterReading


def map_electricity_meter_readings(
    meter_id: str, response: dict[str, Any]
) -> tuple[ElectricityMeterReading, ...]:
    edges = ((response.get("data") or {}).get(
        "electricityMeterReadings") or {}).get("edges") or []
    readings_by_register: dict[str, ElectricityMeterReading] = {}
    for edge in edges:
        node = edge.get("node") or {}
        register_obis_code = node.get("registerObisCode")
        if node.get("value") is None or not register_obis_code:
            continue
        read_at = node.get("readAt")
        reading = ElectricityMeterReading(
            meter_id=meter_id,
            value=Decimal(str(node["value"])),
            read_at=datetime.fromisoformat(
                read_at.replace("Z", "+00:00")) if read_at else None,
            register_obis_code=register_obis_code,
            register_type=node.get("registerType"),
        )
        current = readings_by_register.get(register_obis_code)
        if current is None or (reading.read_at or datetime.min.replace(tzinfo=UTC)) > (
            current.read_at or datetime.min.replace(tzinfo=UTC)
        ):
            readings_by_register[register_obis_code] = reading
    return tuple(readings_by_register.values())


def map_latest_electricity_meter_reading(
    meter_id: str, response: dict[str, Any]
) -> ElectricityMeterReading | None:
    """Return the most recent meter reading across all available registers."""
    readings = map_electricity_meter_readings(meter_id, response)
    return max(readings, key=lambda reading: reading.read_at or datetime.min.replace(tzinfo=UTC), default=None)

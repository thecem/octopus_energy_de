"""Historical electricity consumption action."""

from __future__ import annotations

from datetime import date
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from ..api.models.tariff import ElectricitySupply
from ..const import DOMAIN

SCHEMA = vol.Schema(
    {
        vol.Required("date"): str,
        vol.Optional("supply_point_id"): str,
    }
)


def matching_supplies(
    hass: HomeAssistant, supply_point_id: str | None
) -> list[tuple[Any, ElectricitySupply]]:
    """Return configured supplies that match an optional supply point ID."""
    matches: list[tuple[Any, ElectricitySupply]] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = entry.runtime_data
        if not runtime:
            continue
        for supply in runtime.coordinator.data.electricity:
            if supply.property_id and (
                supply_point_id is None or supply.supply_point_id == supply_point_id
            ):
                matches.append((runtime, supply))
    return matches


async def async_get_electricity_consumption(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, object]:
    """Return consumption intervals for an explicitly requested day."""
    try:
        measurement_date = date.fromisoformat(call.data["date"])
    except ValueError as err:
        raise HomeAssistantError("date must use YYYY-MM-DD") from err

    results: list[dict[str, object]] = []
    for runtime, supply in matching_supplies(hass, call.data.get("supply_point_id")):
        consumption = await runtime.client.electricity_consumption(
            runtime.coordinator.account_number, supply.property_id, measurement_date
        )
        results.append(
            {
                "supply_point_id": supply.supply_point_id,
                "date": consumption.date.isoformat(),
                "total_kwh": str(sum((interval.value for interval in consumption.intervals), 0)),
                "intervals": [
                    {
                        "start": interval.start.isoformat(),
                        "end": interval.end.isoformat(),
                        "consumption_kwh": str(interval.value),
                    }
                    for interval in consumption.intervals
                ],
            }
        )
    if not results:
        raise HomeAssistantError("No matching electricity supply was found")
    return {"consumption": results}

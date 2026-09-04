"""Electricity consumption CSV export action."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .consumption import matching_supplies

SCHEMA = vol.Schema(
    {
        vol.Required("start_date"): str,
        vol.Required("end_date"): str,
        vol.Optional("supply_point_id"): str,
        vol.Optional("directory", default="octopus_energy_de_exports"): str,
    }
)


def write_consumption_csv(path: Path, metadata: dict[str, str], rows: list[dict[str, str]]) -> None:
    """Write compact consumption rows with one metadata block."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        for key, value in metadata.items():
            file.write(f"# {key}={value}\n")
        writer = csv.DictWriter(
            file, fieldnames=["date", "start", "end", "consumption_kwh"])
        writer.writeheader()
        writer.writerows(rows)


def export_directory(hass: HomeAssistant, directory: str) -> tuple[Path, str]:
    """Resolve a user-selected directory safely below config/www."""
    relative = Path(directory)
    if relative.is_absolute() or ".." in relative.parts:
        raise HomeAssistantError(
            "directory must be a relative path below config/www")
    return Path(hass.config.path("www", relative)), relative.as_posix()


async def async_export_electricity_consumption_csv(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, str | int]:
    """Export an explicitly requested period for exactly one supply."""
    try:
        start_date = date.fromisoformat(call.data["start_date"])
        end_date = date.fromisoformat(call.data["end_date"])
    except ValueError as err:
        raise HomeAssistantError(
            "start_date and end_date must use YYYY-MM-DD") from err
    if end_date < start_date or (end_date - start_date).days > 30:
        raise HomeAssistantError(
            "The export period must be between 1 and 31 days")

    supplies = matching_supplies(hass, call.data.get("supply_point_id"))
    if not supplies:
        raise HomeAssistantError("No matching electricity supply was found")
    if len(supplies) > 1:
        raise HomeAssistantError(
            "Set supply_point_id when more than one electricity supply is available")

    runtime, supply = supplies[0]
    rows: list[dict[str, str]] = []
    for offset in range((end_date - start_date).days + 1):
        measurement_date = date.fromordinal(start_date.toordinal() + offset)
        consumption = await runtime.client.electricity_consumption(
            runtime.coordinator.account_number, supply.property_id, measurement_date
        )
        rows.extend(
            {
                "date": measurement_date.isoformat(),
                "start": interval.start.isoformat(),
                "end": interval.end.isoformat(),
                "consumption_kwh": str(interval.value),
            }
            for interval in consumption.intervals
        )
    if not rows:
        raise HomeAssistantError(
            "No consumption data was available for the selected period")

    directory, url_directory = export_directory(hass, call.data["directory"])
    filename = f"octopus_energy_de_consumption_{start_date}_{end_date}.csv"
    meter_ids = {meter.meter_id for meter in supply.meters}
    metadata = {
        "measurement_scope": "property",
        "supply_point_id": supply.supply_point_id,
        "meter_numbers": ",".join(meter.number or meter.meter_id for meter in supply.meters),
        "obis_registers": ",".join(
            sorted(
                reading.register_obis_code
                for reading in runtime.meter_coordinator.data.electricity_meter_readings
                if reading.meter_id in meter_ids and reading.register_obis_code
            )
        ),
    }
    output_path = directory / filename
    await hass.async_add_executor_job(write_consumption_csv, output_path, metadata, rows)
    url = f"/local/{url_directory}/{filename}"
    await hass.services.async_call(
        "persistent_notification",
        "create",
        {
            "title": "Octopus Energy DE export ready",
            "message": f"[Download CSV]({url})",
            "notification_id": "octopus_energy_de_consumption_export",
        },
        blocking=True,
    )
    return {"url": url, "rows": len(rows)}

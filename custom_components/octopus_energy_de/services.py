"""Explicit SmartFlex service handlers."""

from __future__ import annotations

import csv
from datetime import date, time
from functools import partial
from pathlib import Path

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

SERVICE_SET_DEVICE_PREFERENCES = "set_device_preferences"
SERVICE_GET_ELECTRICITY_CONSUMPTION = "get_electricity_consumption"
SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV = "export_electricity_consumption_csv"
SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): str,
        vol.Required("target_percentage"): vol.All(vol.Coerce(int), vol.Range(min=20, max=100)),
        vol.Required("target_time"): str,
    }
)
CONSUMPTION_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("date"): str,
        vol.Optional("supply_point_id"): str,
    }
)
CONSUMPTION_EXPORT_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required("start_date"): str,
        vol.Required("end_date"): str,
        vol.Optional("supply_point_id"): str,
        vol.Optional("directory", default="octopus_energy_de_exports"): str,
    }
)


def _validate_target_time(value: str) -> str:
    try:
        parsed = time.fromisoformat(value)
    except ValueError as err:
        raise HomeAssistantError(
            "target_time must use HH:MM or HH:MM:SS") from err
    if not 4 <= parsed.hour <= 17:
        raise HomeAssistantError("target_time must be between 04:00 and 17:59")
    return parsed.strftime("%H:%M")


async def async_set_device_preferences(hass: HomeAssistant, call: ServiceCall) -> None:
    device_id = call.data["device_id"]
    target_time = _validate_target_time(call.data["target_time"])
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = entry.runtime_data
        if runtime and any(
            device.device_id == device_id for device in runtime.smartflex_coordinator.data.devices
        ):
            await runtime.client.set_device_preferences(
                device_id, call.data["target_percentage"], target_time
            )
            await runtime.smartflex_coordinator.async_request_refresh()
            return
    raise HomeAssistantError(
        "SmartFlex device was not found in an active Octopus Energy DE entry")


async def async_get_electricity_consumption(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, object]:
    try:
        measurement_date = date.fromisoformat(call.data["date"])
    except ValueError as err:
        raise HomeAssistantError("date must use YYYY-MM-DD") from err

    results: list[dict[str, object]] = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = entry.runtime_data
        if not runtime:
            continue
        supplies = runtime.coordinator.data.electricity
        requested_supply = call.data.get("supply_point_id")
        if requested_supply:
            supplies = tuple(
                supply for supply in supplies if supply.supply_point_id == requested_supply)
        for supply in supplies:
            if not supply.property_id:
                continue
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


def _export_directory(hass: HomeAssistant, directory: str) -> tuple[Path, str]:
    relative = Path(directory)
    if relative.is_absolute() or ".." in relative.parts:
        raise HomeAssistantError(
            "directory must be a relative path below config/www")
    return Path(hass.config.path("www", relative)), relative.as_posix()


def _write_consumption_csv(
    path: Path, metadata: dict[str, str], rows: list[dict[str, str]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        for key, value in metadata.items():
            file.write(f"# {key}={value}\n")
        writer = csv.DictWriter(
            file,
            fieldnames=["date", "start", "end", "consumption_kwh"],
        )
        writer.writeheader()
        writer.writerows(rows)


async def async_export_electricity_consumption_csv(
    hass: HomeAssistant, call: ServiceCall
) -> dict[str, str | int]:
    try:
        start_date = date.fromisoformat(call.data["start_date"])
        end_date = date.fromisoformat(call.data["end_date"])
    except ValueError as err:
        raise HomeAssistantError(
            "start_date and end_date must use YYYY-MM-DD") from err
    if end_date < start_date or (end_date - start_date).days > 30:
        raise HomeAssistantError(
            "The export period must be between 1 and 31 days")

    requested_supply = call.data.get("supply_point_id")
    selected_supplies = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        runtime = entry.runtime_data
        if not runtime:
            continue
        supplies = runtime.coordinator.data.electricity
        if requested_supply:
            supplies = tuple(
                supply for supply in supplies if supply.supply_point_id == requested_supply)
        for supply in supplies:
            if supply.property_id:
                selected_supplies.append((runtime, supply))
    if not selected_supplies:
        raise HomeAssistantError("No matching electricity supply was found")
    if len(selected_supplies) > 1:
        raise HomeAssistantError(
            "Set supply_point_id when more than one electricity supply is available")

    runtime, supply = selected_supplies[0]
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

    directory, url_directory = _export_directory(hass, call.data["directory"])
    filename = f"octopus_energy_de_consumption_{start_date}_{end_date}.csv"
    output_path = directory / filename
    meter_readings = runtime.meter_coordinator.data.electricity_meter_readings
    meter_ids = {meter.meter_id for meter in supply.meters}
    metadata = {
        "measurement_scope": "property",
        "supply_point_id": supply.supply_point_id,
        "meter_numbers": ",".join(meter.number or meter.meter_id for meter in supply.meters),
        "obis_registers": ",".join(
            sorted(
                reading.register_obis_code
                for reading in meter_readings
                if reading.meter_id in meter_ids and reading.register_obis_code
            )
        ),
    }
    await hass.async_add_executor_job(_write_consumption_csv, output_path, metadata, rows)
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


def async_register_services(hass: HomeAssistant) -> None:
    if not hass.services.has_service(DOMAIN, SERVICE_SET_DEVICE_PREFERENCES):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SET_DEVICE_PREFERENCES,
            partial(async_set_device_preferences, hass),
            schema=SERVICE_SCHEMA,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_GET_ELECTRICITY_CONSUMPTION,
            partial(async_get_electricity_consumption, hass),
            schema=CONSUMPTION_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )
        hass.services.async_register(
            DOMAIN,
            SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV,
            partial(async_export_electricity_consumption_csv, hass),
            schema=CONSUMPTION_EXPORT_SERVICE_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )


def async_unregister_services(hass: HomeAssistant) -> None:
    hass.services.async_remove(DOMAIN, SERVICE_SET_DEVICE_PREFERENCES)
    hass.services.async_remove(DOMAIN, SERVICE_GET_ELECTRICITY_CONSUMPTION)
    hass.services.async_remove(
        DOMAIN, SERVICE_EXPORT_ELECTRICITY_CONSUMPTION_CSV)

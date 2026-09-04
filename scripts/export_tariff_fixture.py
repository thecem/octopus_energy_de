#!/usr/bin/env python3
"""Export a minimal anonymized tariff fixture from Kraken.

Run inside the devcontainer after setting OCTOPUS_EMAIL and OCTOPUS_PASSWORD.
No credentials are written to disk. Supply point/account identifiers are omitted.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import aiohttp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from custom_components.octopus_energy_de.api.client import OctopusEnergyDEClient  # noqa: E402
from custom_components.octopus_energy_de.api.graphql.queries import (  # noqa: E402
    ELECTRICITY_CONSUMPTION_QUERY,
    TARIFF_QUERY,
)


def minimize(response: dict) -> dict:
    account = (response.get("data") or {}).get("account") or {}
    agreements: list[dict] = []
    for prop in account.get("allProperties") or []:
        for malo in prop.get("electricityMalos") or []:
            for agreement in malo.get("agreements") or []:
                agreements.append(
                    {
                        "product": agreement.get("product"),
                        "unitRateInformation": agreement.get("unitRateInformation"),
                        "unitRateForecast": agreement.get("unitRateForecast"),
                        "validFrom": agreement.get("validFrom"),
                        "validTo": agreement.get("validTo"),
                    }
                )
    return {"schema": 1, "agreements": agreements}


def minimize_measurements(response: dict) -> list[dict]:
    measurements = (((response.get("data") or {}).get("account") or {}).get("property") or {}).get(
        "measurements"
    ) or {}
    raw_intervals: list[tuple[datetime, datetime, str | None]] = []
    for edge in measurements.get("edges") or []:
        node = edge.get("node") or {}
        start = node.get("startAt")
        end = node.get("endAt")
        if start and end:
            raw_intervals.append(
                (
                    datetime.fromisoformat(start.replace("Z", "+00:00")),
                    datetime.fromisoformat(end.replace("Z", "+00:00")),
                    node.get("unit"),
                )
            )

    if not raw_intervals:
        return []

    reference = min(start for start, _, _ in raw_intervals)
    return [
        {
            "start_offset_seconds": int((start - reference).total_seconds()),
            "end_offset_seconds": int((end - reference).total_seconds()),
            "unit": unit,
        }
        for start, end, unit in raw_intervals
    ]


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--account", help="Account number; if omitted, the first account is used")
    parser.add_argument(
        "--measurements-date",
        type=date.fromisoformat,
        default=date.today() - timedelta(days=1),
        help="Date to export electricity interval structure for (default: yesterday)",
    )
    args = parser.parse_args()

    email = os.environ.get("OCTOPUS_EMAIL")
    password = os.environ.get("OCTOPUS_PASSWORD")
    if not email or not password:
        raise SystemExit("Set OCTOPUS_EMAIL and OCTOPUS_PASSWORD in the environment")

    async with aiohttp.ClientSession() as session:
        client = OctopusEnergyDEClient(session, email, password)
        accounts = await client.accounts()
        if not accounts:
            raise SystemExit("No accounts returned")
        account = args.account or accounts[0]["number"]
        token = await client.auth.ensure_token()
        raw = await client.transport.execute(
            TARIFF_QUERY,
            variables={"accountNumber": account},
            token=token,
        )

        properties = ((raw.get("data") or {}).get("account") or {}).get("allProperties") or []
        measurement_intervals: list[dict] = []
        for property_data in properties:
            property_id = property_data.get("id")
            if not property_id:
                continue
            measurements = await client.transport.execute(
                ELECTRICITY_CONSUMPTION_QUERY,
                variables={
                    "accountNumber": account,
                    "propertyId": property_id,
                    "date": args.measurements_date.isoformat(),
                },
                token=token,
            )
            measurement_intervals.extend(minimize_measurements(measurements))

    fixture = minimize(raw)
    fixture["electricity_measurement_intervals"] = measurement_intervals
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(fixture['agreements'])} anonymized agreement(s) to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

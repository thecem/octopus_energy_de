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
from pathlib import Path

import aiohttp

from custom_components.octopus_energy_de.api.client import OctopusEnergyDEClient
from custom_components.octopus_energy_de.api.graphql.queries import TARIFF_QUERY


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


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--account", help="Account number; if omitted, the first account is used")
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

    fixture = minimize(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {len(fixture['agreements'])} anonymized agreement(s) to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())

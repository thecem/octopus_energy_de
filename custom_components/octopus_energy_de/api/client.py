"""High-level Octopus Energy Germany API client."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import aiohttp

from .auth import OctopusAuth
from .exceptions import OctopusEnergyDEError
from .graphql.queries import (
    ACCOUNT_DISCOVERY_QUERY,
    ELECTRICITY_CONSUMPTION_QUERY,
    ELECTRICITY_METER_READINGS_QUERY,
    SMARTFLEX_QUERY,
    TARIFF_QUERY,
)
from .graphql.transport import GraphQLTransport
from .mappers.account import map_account_snapshot
from .mappers.consumption import map_electricity_consumption
from .mappers.meter import map_electricity_meter_readings
from .mappers.smartflex import map_smartflex_snapshot
from .models.smartflex import SmartFlexSnapshot
from .models.tariff import AccountSnapshot, ElectricityConsumption, ElectricityMeterReading

_LOGGER = logging.getLogger(__name__)


class OctopusEnergyDEClient:
    """Small API facade. Domain-specific clients can be split out as features grow."""

    def __init__(self, session: aiohttp.ClientSession, email: str, password: str) -> None:
        self.transport = GraphQLTransport(session)
        self.auth = OctopusAuth(self.transport, email, password)

    async def accounts(self) -> list[dict[str, Any]]:
        token = await self.auth.ensure_token()
        result = await self.transport.execute(ACCOUNT_DISCOVERY_QUERY, token=token)
        return ((result.get("data") or {}).get("viewer") or {}).get("accounts") or []

    async def account_snapshot(self, account_number: str) -> AccountSnapshot:
        token = await self.auth.ensure_token()
        result = await self.transport.execute(
            TARIFF_QUERY,
            variables={"accountNumber": account_number},
            token=token,
        )
        snapshot = map_account_snapshot(account_number, result)
        readings: list[ElectricityMeterReading] = []
        consumption: list[ElectricityConsumption] = []
        smartflex = SmartFlexSnapshot()
        for supply in snapshot.electricity:
            for meter in supply.meters:
                readings.extend(
                    await self.electricity_meter_readings(
                        account_number, meter.meter_id, token
                    )
                )
            if supply.property_id and not any(
                item.property_id == supply.property_id for item in consumption
            ):
                consumption.append(
                    await self.previous_day_electricity_consumption(
                        account_number, supply.property_id, token
                    )
                )
        try:
            smartflex = await self.smartflex_snapshot(account_number, token)
        except OctopusEnergyDEError as err:
            _LOGGER.debug("SmartFlex data unavailable for account: %s", err)
        return AccountSnapshot(
            account_number=snapshot.account_number,
            electricity=snapshot.electricity,
            electricity_meter_readings=tuple(readings),
            electricity_consumption=tuple(consumption),
            smartflex=smartflex,
        )

    async def electricity_meter_readings(
        self, account_number: str, meter_id: str, token: str | None = None
    ) -> tuple[ElectricityMeterReading, ...]:
        result = await self.transport.execute(
            ELECTRICITY_METER_READINGS_QUERY,
            variables={"accountNumber": account_number, "meterId": meter_id},
            token=token or await self.auth.ensure_token(),
        )
        return map_electricity_meter_readings(meter_id, result)

    async def previous_day_electricity_consumption(
        self, account_number: str, property_id: str, token: str | None = None
    ) -> ElectricityConsumption:
        measurement_date = date.today() - timedelta(days=1)
        result = await self.transport.execute(
            ELECTRICITY_CONSUMPTION_QUERY,
            variables={
                "accountNumber": account_number,
                "propertyId": property_id,
                "date": measurement_date.isoformat(),
            },
            token=token or await self.auth.ensure_token(),
        )
        return map_electricity_consumption(property_id, measurement_date, result)

    async def smartflex_snapshot(
        self, account_number: str, token: str | None = None
    ) -> SmartFlexSnapshot:
        result = await self.transport.execute(
            SMARTFLEX_QUERY,
            variables={"accountNumber": account_number},
            token=token or await self.auth.ensure_token(),
        )
        return map_smartflex_snapshot(result)

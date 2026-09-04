"""High-level Octopus Energy Germany API client."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import aiohttp

from .auth import OctopusAuth
from .graphql.queries import (
    ACCOUNT_DISCOVERY_QUERY,
    BOOST_CHARGE_MUTATION,
    ELECTRICITY_CONSUMPTION_QUERY,
    ELECTRICITY_METER_READINGS_QUERY,
    SMART_CONTROL_MUTATION,
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
        return map_account_snapshot(account_number, result)

    async def meter_snapshot(
        self, account_number: str, supplies: tuple
    ) -> AccountSnapshot:
        token = await self.auth.ensure_token()
        readings: list[ElectricityMeterReading] = []
        for supply in supplies:
            for meter in supply.meters:
                readings.extend(
                    await self.electricity_meter_readings(
                        account_number, meter.meter_id, token
                    )
                )
        return AccountSnapshot(
            account_number=account_number,
            electricity=supplies,
            electricity_meter_readings=tuple(readings),
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

    async def electricity_consumption(
        self, account_number: str, property_id: str, measurement_date: date, token: str | None = None
    ) -> ElectricityConsumption:
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

    async def set_smart_control(self, device_id: str, enabled: bool) -> None:
        await self.transport.execute(
            SMART_CONTROL_MUTATION,
            variables={"deviceId": device_id,
                       "action": "UNSUSPEND" if enabled else "SUSPEND"},
            token=await self.auth.ensure_token(),
        )

    async def set_boost_charge(self, device_id: str, enabled: bool) -> None:
        await self.transport.execute(
            BOOST_CHARGE_MUTATION,
            variables={"input": {"deviceId": device_id,
                                 "action": "BOOST" if enabled else "CANCEL"}},
            token=await self.auth.ensure_token(),
        )

    async def set_device_preferences(
        self, device_id: str, target_percentage: int, target_time: str
    ) -> None:
        schedules = "\n".join(
            f'{{ dayOfWeek: {day}, time: "{target_time}", max: {target_percentage} }}'
            for day in ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")
        )
        mutation = f"""
        mutation SetDevicePreferences {{
          setDevicePreferences(input: {{
            deviceId: "{device_id}",
            mode: CHARGE,
            unit: PERCENTAGE,
            schedules: [{schedules}]
          }}) {{ id }}
        }}
        """
        await self.transport.execute(mutation, token=await self.auth.ensure_token())

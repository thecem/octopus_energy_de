"""Electricity meter API operations."""

from __future__ import annotations

from .graphql.meters import ELECTRICITY_METER_READINGS_QUERY
from .mappers.meter import map_electricity_meter_readings
from .models.tariff import AccountSnapshot, ElectricityMeterReading, ElectricitySupply


class MeterOperations:
    """Operations for normalized meter snapshots and register readings."""

    async def meter_snapshot(
        self, account_number: str, supplies: tuple[ElectricitySupply, ...]
    ) -> AccountSnapshot:
        token = await self.auth.ensure_token()
        readings: list[ElectricityMeterReading] = []
        for supply in supplies:
            for meter in supply.meters:
                readings.extend(await self.electricity_meter_readings(account_number, meter.meter_id, token))
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
"""Electricity consumption API operations."""

from __future__ import annotations

from datetime import date

from .graphql.consumption import ELECTRICITY_CONSUMPTION_QUERY
from .mappers.consumption import map_electricity_consumption
from .models.tariff import ElectricityConsumption


class ConsumptionOperations:
    """Operations for requested historical consumption periods."""

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

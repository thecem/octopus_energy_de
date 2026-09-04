"""SmartFlex read and control API operations."""

from __future__ import annotations

from .graphql.smartflex import BOOST_CHARGE_MUTATION, SMART_CONTROL_MUTATION, SMARTFLEX_QUERY
from .mappers.smartflex import map_smartflex_snapshot
from .models.smartflex import SmartFlexSnapshot


class SmartFlexOperations:
    """Read and explicitly control supported SmartFlex features."""

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
            variables={"deviceId": device_id, "action": "UNSUSPEND" if enabled else "SUSPEND"},
            token=await self.auth.ensure_token(),
        )

    async def set_boost_charge(self, device_id: str, enabled: bool) -> None:
        await self.transport.execute(
            BOOST_CHARGE_MUTATION,
            variables={
                "input": {"deviceId": device_id, "action": "BOOST" if enabled else "CANCEL"}
            },
            token=await self.auth.ensure_token(),
        )

    async def set_device_preferences(
        self, device_id: str, target_percentage: int, target_time: str
    ) -> None:
        schedules = "\n".join(
            f'{{ dayOfWeek: {day}, time: "{target_time}", max: {target_percentage} }}'
            for day in (
                "MONDAY",
                "TUESDAY",
                "WEDNESDAY",
                "THURSDAY",
                "FRIDAY",
                "SATURDAY",
                "SUNDAY",
            )
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

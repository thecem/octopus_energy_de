"""Account and tariff API operations."""

from __future__ import annotations

from typing import Any

from .graphql.account import ACCOUNT_DISCOVERY_QUERY, TARIFF_QUERY
from .mappers.account import map_account_snapshot
from .models.tariff import AccountSnapshot


class AccountOperations:
    """Operations for account discovery and normalized tariff snapshots."""

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

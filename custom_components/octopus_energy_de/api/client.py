"""High-level Octopus Energy Germany API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from .auth import OctopusAuth
from .graphql.queries import ACCOUNT_DISCOVERY_QUERY, TARIFF_QUERY
from .graphql.transport import GraphQLTransport
from .mappers.account import map_account_snapshot
from .models.tariff import AccountSnapshot


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

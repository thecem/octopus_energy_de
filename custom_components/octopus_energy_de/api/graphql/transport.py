"""Low-level GraphQL transport."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from ...const import GRAPHQL_ENDPOINT, REQUEST_TIMEOUT
from ..exceptions import CannotConnectError, GraphQLError


class GraphQLTransport:
    """Execute GraphQL requests without domain knowledge."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session

    async def execute(
        self,
        query: str,
        *,
        variables: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = token

        payload = {"query": query, "variables": variables or {}}
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.post(
                    GRAPHQL_ENDPOINT,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                result: dict[str, Any] = await response.json()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise CannotConnectError(str(err)) from err

        errors = result.get("errors")
        if errors:
            message = "; ".join(str(item.get("message", item)) for item in errors)
            raise GraphQLError(message)
        return result

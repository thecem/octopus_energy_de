"""Authentication against Octopus Germany Kraken."""

from __future__ import annotations

import asyncio
import base64
import json
import time
from typing import Any

from ..const import TOKEN_REFRESH_MARGIN_SECONDS
from .exceptions import AuthenticationError
from .graphql.queries import TOKEN_MUTATION
from .graphql.transport import GraphQLTransport


class OctopusAuth:
    """Manage a Kraken token for one set of credentials."""

    def __init__(self, transport: GraphQLTransport, email: str, password: str) -> None:
        self._transport = transport
        self._email = email
        self._password = password
        self._token: str | None = None
        self._expires_at: float = 0
        self._lock = asyncio.Lock()

    @property
    def token(self) -> str | None:
        return self._token

    def _is_valid(self) -> bool:
        return bool(self._token) and time.time() < self._expires_at - TOKEN_REFRESH_MARGIN_SECONDS

    async def ensure_token(self) -> str:
        if self._is_valid() and self._token:
            return self._token
        async with self._lock:
            if self._is_valid() and self._token:
                return self._token
            result = await self._transport.execute(
                TOKEN_MUTATION,
                variables={"email": self._email, "password": self._password},
            )
            auth = (result.get("data") or {}).get("obtainKrakenToken") or {}
            token = auth.get("token")
            if not token:
                raise AuthenticationError("Kraken did not return an authentication token")
            self._token = token
            payload = auth.get("payload") or {}
            self._expires_at = float(payload.get("exp") or self._decode_exp(token) or (time.time() + 3600))
            return token

    @staticmethod
    def _decode_exp(token: str) -> float | None:
        """Read JWT expiry without verifying the signature; token trust comes from HTTPS Kraken response."""
        try:
            part = token.split(".")[1]
            part += "=" * (-len(part) % 4)
            payload: dict[str, Any] = json.loads(base64.urlsafe_b64decode(part).decode())
            return float(payload["exp"]) if "exp" in payload else None
        except (IndexError, ValueError, KeyError, json.JSONDecodeError):
            return None

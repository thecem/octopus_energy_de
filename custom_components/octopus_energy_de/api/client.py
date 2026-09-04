"""Public Octopus Energy DE API client facade."""

from __future__ import annotations

import aiohttp

from .account import AccountOperations
from .auth import OctopusAuth
from .consumption import ConsumptionOperations
from .graphql.transport import GraphQLTransport
from .meters import MeterOperations
from .smartflex import SmartFlexOperations


class OctopusEnergyDEClient(
    AccountOperations,
    MeterOperations,
    ConsumptionOperations,
    SmartFlexOperations,
):
    """Compose focused API operations behind the stable client interface."""

    def __init__(self, session: aiohttp.ClientSession, email: str, password: str) -> None:
        self.transport = GraphQLTransport(session)
        self.auth = OctopusAuth(self.transport, email, password)

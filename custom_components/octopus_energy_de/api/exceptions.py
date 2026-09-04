"""API exceptions."""


class OctopusEnergyDEError(Exception):
    """Base error."""


class AuthenticationError(OctopusEnergyDEError):
    """Authentication failed."""


class GraphQLError(OctopusEnergyDEError):
    """GraphQL request failed."""


class CannotConnectError(OctopusEnergyDEError):
    """Connection to Kraken failed."""

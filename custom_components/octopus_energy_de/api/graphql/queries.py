"""Compatibility reexports for GraphQL operations."""

from .smartflex import BOOST_CHARGE_MUTATION, SMART_CONTROL_MUTATION, SMARTFLEX_QUERY
from .meters import ELECTRICITY_METER_READINGS_QUERY
from .consumption import ELECTRICITY_CONSUMPTION_QUERY
from .account import ACCOUNT_DISCOVERY_QUERY, TARIFF_QUERY
TOKEN_MUTATION = """
mutation krakenTokenAuthentication($email: String!, $password: String!) {
  obtainKrakenToken(input: { email: $email, password: $password }) {
    token
    payload
  }
}
"""

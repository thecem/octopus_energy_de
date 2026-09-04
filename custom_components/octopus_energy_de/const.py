"""Constants for Octopus Energy DE."""

from datetime import timedelta

DOMAIN = "octopus_energy_de"
NAME = "Octopus Energy DE"
VERSION = "0.1.0"

CONF_ACCOUNT_NUMBER = "account_number"

GRAPHQL_ENDPOINT = "https://api.oeg-kraken.energy/v1/graphql/"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)
REQUEST_TIMEOUT = 30
TOKEN_REFRESH_MARGIN_SECONDS = 300

PLATFORMS = ["sensor"]

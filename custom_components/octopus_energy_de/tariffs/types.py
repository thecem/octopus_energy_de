"""Tariff classifications."""

from enum import StrEnum


class TariffType(StrEnum):
    FIXED = "fixed"
    TIME_OF_USE = "time_of_use"
    DYNAMIC = "dynamic"
    UNKNOWN = "unknown"


class TariffFamily(StrEnum):
    GENERIC_FIXED = "generic_fixed"
    OCTOPUS_GO = "octopus_go"
    OCTOPUS_HEAT = "octopus_heat"
    DYNAMIC_OCTOPUS = "dynamic_octopus"
    INTELLIGENT_OCTOPUS = "intelligent_octopus"
    INTELLIGENT_OCTOPUS_GO_LEGACY = "intelligent_octopus_go_legacy"
    UNKNOWN = "unknown"

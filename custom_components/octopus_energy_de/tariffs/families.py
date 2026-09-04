"""Marketing family detection, kept separate from technical tariff behavior."""

from __future__ import annotations

import re

from .types import TariffFamily


def detect_family(code: str, name: str | None = None, description: str | None = None) -> TariffFamily:
    value = " ".join(x or "" for x in (code, name, description)).lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", value)
    if "intelligent" in normalized and re.search(r"\bgo\b", normalized):
        return TariffFamily.INTELLIGENT_OCTOPUS_GO_LEGACY
    if "dynamic" in normalized:
        return TariffFamily.DYNAMIC_OCTOPUS
    if "heat" in normalized:
        return TariffFamily.OCTOPUS_HEAT
    if "intelligent" in normalized:
        return TariffFamily.INTELLIGENT_OCTOPUS
    if re.search(r"\bgo\b", normalized):
        return TariffFamily.OCTOPUS_GO
    return TariffFamily.UNKNOWN

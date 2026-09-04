"""Map account query responses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..models.tariff import AccountSnapshot, ElectricitySupply
from .tariff import map_tariff


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _active_agreement(agreements: list[dict[str, Any]], now: datetime) -> dict[str, Any] | None:
    active: list[dict[str, Any]] = []
    for agreement in agreements:
        start = _parse(agreement.get("validFrom"))
        end = _parse(agreement.get("validTo"))
        if (start is None or start <= now) and (end is None or now < end):
            active.append(agreement)
    if active:
        return max(active, key=lambda item: _parse(item.get("validFrom")) or datetime.min.replace(tzinfo=timezone.utc))
    return max(agreements, key=lambda item: _parse(item.get("validFrom")) or datetime.min.replace(tzinfo=timezone.utc), default=None)


def map_account_snapshot(account_number: str, response: dict[str, Any]) -> AccountSnapshot:
    account = (response.get("data") or {}).get("account") or {}
    supplies: list[ElectricitySupply] = []
    now = datetime.now(timezone.utc)
    for property_data in account.get("allProperties") or []:
        for malo in property_data.get("electricityMalos") or []:
            agreement = _active_agreement(malo.get("agreements") or [], now)
            if agreement:
                supplies.append(
                    ElectricitySupply(
                        supply_point_id=malo.get("maloNumber") or property_data.get("id") or "electricity",
                        tariff=map_tariff(agreement),
                    )
                )
    return AccountSnapshot(account_number=account_number, electricity=tuple(supplies))

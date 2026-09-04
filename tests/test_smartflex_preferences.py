import asyncio

import pytest

from custom_components.octopus_energy_de.actions.preferences import validate_target_time
from custom_components.octopus_energy_de.api.client import OctopusEnergyDEClient


class _Auth:
    async def ensure_token(self) -> str:
        return "token"


class _Transport:
    def __init__(self) -> None:
        self.query = ""

    async def execute(self, query: str, *, token: str) -> dict:
        self.query = query
        return {"data": {}}


def test_device_preferences_use_all_days_and_normalized_time():
    client = OctopusEnergyDEClient.__new__(OctopusEnergyDEClient)
    transport = _Transport()
    client.transport = transport
    client.auth = _Auth()

    asyncio.run(client.set_device_preferences("device", 80, "06:30"))

    assert 'deviceId: "device"' in transport.query
    assert transport.query.count('time: "06:30"') == 7


def test_target_time_is_limited_to_supported_window():
    assert validate_target_time("06:30:00") == "06:30"
    with pytest.raises(Exception, match="04:00"):
        validate_target_time("03:59")

import asyncio

from custom_components.octopus_energy_de.api.client import OctopusEnergyDEClient


class _Auth:
    async def ensure_token(self) -> str:
        return "token"


class _Transport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict, str]] = []

    async def execute(self, query: str, *, variables: dict, token: str) -> dict:
        self.calls.append((query, variables, token))
        return {"data": {}}


def _client() -> tuple[OctopusEnergyDEClient, _Transport]:
    client = OctopusEnergyDEClient.__new__(OctopusEnergyDEClient)
    transport = _Transport()
    client.transport = transport
    client.auth = _Auth()
    return client, transport


def test_smartflex_control_mutations_use_explicit_actions():
    client, transport = _client()

    asyncio.run(client.set_smart_control("device", enabled=False))
    asyncio.run(client.set_boost_charge("device", enabled=True))

    assert transport.calls[0][1] == {"deviceId": "device", "action": "SUSPEND"}
    assert transport.calls[1][1] == {
        "input": {"deviceId": "device", "action": "BOOST"}}

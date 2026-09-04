import asyncio
from types import SimpleNamespace

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from custom_components.octopus_energy_de import config_flow


def test_reauth_replaces_credentials_without_recreating_entry(monkeypatch):
    entry = SimpleNamespace(
        data={CONF_EMAIL: "old@example.invalid",
              CONF_PASSWORD: "old-password", "account_number": "account"}
    )
    updated_entries = []
    hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_update_entry=lambda updated_entry, data: updated_entries.append(
                (updated_entry, data))
        )
    )

    class Client:
        def __init__(self, *_args) -> None:
            pass

        async def accounts(self) -> list[dict[str, str]]:
            return [{"number": "account"}]

    monkeypatch.setattr(config_flow, "OctopusEnergyDEClient", Client)
    monkeypatch.setattr(
        config_flow, "async_get_clientsession", lambda _hass: None)
    flow = config_flow.OctopusEnergyDEConfigFlow()
    flow.hass = hass
    flow._reauth_entry = entry

    asyncio.run(
        flow.async_step_reauth_confirm(
            {CONF_EMAIL: "new@example.invalid", CONF_PASSWORD: "new-password"}
        )
    )

    assert updated_entries == [
        (
            entry,
            {CONF_EMAIL: "new@example.invalid",
                CONF_PASSWORD: "new-password", "account_number": "account"},
        )
    ]

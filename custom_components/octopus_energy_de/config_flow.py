"""Config flow for Octopus Energy DE."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.client import OctopusEnergyDEClient
from .api.exceptions import AuthenticationError, CannotConnectError, GraphQLError
from .const import CONF_ACCOUNT_NUMBER, DOMAIN


class OctopusEnergyDEConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._credentials: dict[str, str] = {}
        self._accounts: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            client = OctopusEnergyDEClient(
                async_get_clientsession(self.hass), user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
            )
            try:
                self._accounts = await client.accounts()
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except (CannotConnectError, GraphQLError):
                errors["base"] = "cannot_connect"
            else:
                if not self._accounts:
                    errors["base"] = "no_accounts"
                else:
                    self._credentials = {
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    }
                    if len(self._accounts) == 1:
                        return await self._create_for_account(self._accounts[0]["number"])
                    return await self.async_step_account()

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_account(self, user_input: dict[str, Any] | None = None):
        account_numbers = [item["number"] for item in self._accounts]
        if user_input is not None:
            return await self._create_for_account(user_input[CONF_ACCOUNT_NUMBER])
        return self.async_show_form(
            step_id="account",
            data_schema=vol.Schema(
                {vol.Required(CONF_ACCOUNT_NUMBER): vol.In(account_numbers)}
            ),
        )

    async def _create_for_account(self, account_number: str):
        await self.async_set_unique_id(account_number)
        self._abort_if_unique_id_configured()
        data = {**self._credentials, CONF_ACCOUNT_NUMBER: account_number}
        return self.async_create_entry(title=f"Octopus Energy DE {account_number}", data=data)


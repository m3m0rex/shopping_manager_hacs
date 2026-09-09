"""Config flow for Shopping Manager."""

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .api import ApiError, InvalidAuth, ShoppingManagerApi
from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class ShoppingManagerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Shopping Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate connection
            from homeassistant.helpers.aiohttp_client import async_get_clientsession
            session = async_get_clientsession(self.hass)
            api = ShoppingManagerApi(
                user_input[CONF_HOST], user_input.get(CONF_TOKEN) or None, session
            )
            try:
                await api.get_counts()
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_HOST], data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default="http://localhost:3000"): str,
                vol.Optional(CONF_TOKEN): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): int,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return ShoppingManagerOptionsFlow(entry)


class ShoppingManagerOptionsFlow(OptionsFlow):
    """Options flow for Shopping Manager."""

    def __init__(self, entry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.entry.data.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): int,
                vol.Optional(
                    CONF_TOKEN, default=self.entry.data.get(CONF_TOKEN, "")
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)

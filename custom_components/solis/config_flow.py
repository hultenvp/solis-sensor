"""Config flow for Solis integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_CONTROL,
    CONF_KEY_ID,
    CONF_PASSWORD,
    CONF_PLANT_ID,
    CONF_PORTAL_DOMAIN,
    CONF_REFRESH_NOK,
    CONF_REFRESH_OK,
    CONF_SECRET,
    CONF_USERNAME,
    DEFAULT_DOMAIN,
    DOMAIN,
    SENSOR_PREFIX,
)
from .soliscloud_api import SoliscloudAPI, SoliscloudConfig

_LOGGER = logging.getLogger(__name__)


class SolisOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            updated = dict(self.config_entry.data)

            updated[CONF_REFRESH_OK] = user_input.get(CONF_REFRESH_OK, updated.get(CONF_REFRESH_OK, 300))
            updated[CONF_REFRESH_NOK] = user_input.get(CONF_REFRESH_NOK, updated.get(CONF_REFRESH_NOK, 60))

            control_section = user_input.get("Control") or {}
            updated[CONF_CONTROL] = bool(control_section.get(CONF_CONTROL, updated.get(CONF_CONTROL, False)))

            new_pw = (control_section.get(CONF_PASSWORD) or "").strip()
            if new_pw:
                updated[CONF_PASSWORD] = new_pw

            self.hass.config_entries.async_update_entry(self.config_entry, data=updated, title=self.config_entry.title)
            return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required(CONF_REFRESH_OK, default=self.config_entry.data.get(CONF_REFRESH_OK, 300)): cv.positive_int,
                vol.Required(CONF_REFRESH_NOK, default=self.config_entry.data.get(CONF_REFRESH_NOK, 60)): cv.positive_int,
                vol.Required("Control"): data_entry_flow.section(
                    vol.Schema(
                        {
                            vol.Required(CONF_CONTROL, default=self.config_entry.data.get(CONF_CONTROL, False)): bool,
                            vol.Optional(CONF_PASSWORD, default=""): cv.string,
                        }
                    ),
                    {"collapsed": False},
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)


class SolisConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solis."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SolisOptionsFlowHandler:
        return SolisOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = (user_input.get(CONF_NAME) or SENSOR_PREFIX).strip()
            url = (user_input.get(CONF_PORTAL_DOMAIN) or DEFAULT_DOMAIN).strip()

            if not url.startswith("https://"):
                errors["base"] = "invalid_path"
            else:
                self._data = {
                    CONF_NAME: name,
                    CONF_PORTAL_DOMAIN: url,
                }
                return await self.async_step_credentials_secret()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=SENSOR_PREFIX): cv.string,
                vol.Required(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_credentials_secret(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            url = (self._data.get(CONF_PORTAL_DOMAIN) or "").strip()

            plant_id = (user_input.get(CONF_PLANT_ID) or "").strip()
            key_id = (user_input.get(CONF_KEY_ID) or "").strip()
            secret = (user_input.get(CONF_SECRET) or "").strip()

            # Username mag leeg zijn, maar nooit None
            username = (user_input.get(CONF_USERNAME) or "").strip()

            refresh_ok = int(user_input.get(CONF_REFRESH_OK, 300))
            refresh_nok = int(user_input.get(CONF_REFRESH_NOK, 60))

            # Control/password doen we niet in de setup (alleen options),
            # maar we bewaren wel de checkbox zodat entry consistent is.
            control_section = user_input.get("Control") or {}
            control_enabled = bool(control_section.get(CONF_CONTROL, False))
            password = ""  # setup gebruikt geen portal password

            if not url.startswith("https://"):
                errors["base"] = "invalid_path"
            elif not (plant_id and key_id and secret):
                errors["base"] = "missing_fields"
            else:
                await self.async_set_unique_id(plant_id)
                self._abort_if_unique_id_configured()

                self._data.update(
                    {
                        CONF_USERNAME: username,
                        CONF_KEY_ID: key_id,
                        CONF_SECRET: secret,
                        CONF_PLANT_ID: plant_id,
                        CONF_REFRESH_OK: refresh_ok,
                        CONF_REFRESH_NOK: refresh_nok,
                        CONF_CONTROL: control_enabled,
                        CONF_PASSWORD: password,
                    }
                )

                config = SoliscloudConfig(url, username, key_id, secret, plant_id, password)
                api = SoliscloudAPI(config)

                if await api.login(async_get_clientsession(self.hass)):
                    title = getattr(api, "plant_name", None) or f"Station {plant_id}"
                    return self.async_create_entry(title=title, data=self._data)

                errors["base"] = "auth"

        data_schema = vol.Schema(
            {
                vol.Optional(CONF_USERNAME, default=""): cv.string,
                vol.Required(CONF_KEY_ID, default=""): cv.string,
                vol.Required(CONF_SECRET, default=""): cv.string,
                vol.Required(CONF_PLANT_ID, default=""): cv.string,
                vol.Required(CONF_REFRESH_OK, default=300): cv.positive_int,
                vol.Required(CONF_REFRESH_NOK, default=60): cv.positive_int,
                vol.Required("Control"): data_entry_flow.section(
                    vol.Schema(
                        {
                            vol.Required(CONF_CONTROL, default=False): bool,
                            vol.Optional(CONF_PASSWORD, default=""): cv.string,
                        }
                    ),
                    {"collapsed": False},
                ),
            }
        )

        return self.async_show_form(step_id="credentials_secret", data_schema=data_schema, errors=errors)

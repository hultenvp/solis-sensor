"""Config flow for Solis integration."""

import logging
from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import selector

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

SOLISCLOUD = "soliscloud"


class SolisOptionsFlowHandler(OptionsFlow):
    """Handle options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """
        Handle a flow initialized by the user.

        Args:
            user_input: The input received from the user or none.

        Returns:
            The created config entry.
        """
        errors = {}

        if user_input is not None:
            updated_config = dict(self.config_entry.data)

            control_section = user_input.get("Control") or {}
            new_pw = control_section.get(CONF_PASSWORD)

            if new_pw:  # only overwrite if user actually typed something
                updated_config[CONF_PASSWORD] = new_pw

            updated_config[CONF_CONTROL] = control_section.get(
                CONF_CONTROL, updated_config.get(CONF_CONTROL, False))
            updated_config[CONF_REFRESH_OK] = user_input.get(
                CONF_REFRESH_OK, updated_config.get(CONF_REFRESH_OK, 300))
            updated_config[CONF_REFRESH_NOK] = user_input.get(
                CONF_REFRESH_NOK, updated_config.get(CONF_REFRESH_NOK, 60)
            )

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_config,
                title=self.config_entry.title,
            )

        data_schema = {
            vol.Required(CONF_REFRESH_OK, default=self.config_entry.data.get(
                            CONF_REFRESH_OK, 300)): cv.positive_int,
            vol.Required(CONF_REFRESH_NOK, default=self.config_entry.data.get(
                            CONF_REFRESH_NOK, 60)): cv.positive_int,
            vol.Required("Control"): data_entry_flow.section(
                vol.Schema(
                    {
                        vol.Required(CONF_CONTROL, default=self.config_entry.data.get(
                            CONF_CONTROL, False)): bool,
                        vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(
                            CONF_PASSWORD, "")): cv.string,
                    }
                ),
                # Whether or not the section is initially collapsed (default = False)
                {"collapsed": False},
            ),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )


class SolisConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solis."""

    VERSION = 1
    _data = None

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> SolisOptionsFlowHandler:
        """
        Get the options flow for this handler.

        Args:
            config_entry: The ConfigEntry instance.

        Returns:
            The created config flow.
        """
        return SolisOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Select server url and API version."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data = dict(user_input)
            return await self.async_step_credentials_secret()  # no arg

        data_schema = {
            vol.Required(CONF_NAME, default=SENSOR_PREFIX): cv.string,
            vol.Required(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=errors)


    async def async_step_credentials_secret(self, user_input=None):
        errors: dict[str, str] = {}

        if user_input is not None:
            control_section = user_input.get("Control") or {}
            password = control_section.get(CONF_PASSWORD) or user_input.get(CONF_PASSWORD)

            url = self._data.get(CONF_PORTAL_DOMAIN)
            plant_id = user_input.get(CONF_PLANT_ID)
            username = user_input.get(CONF_USERNAME)
            key_id = user_input.get(CONF_KEY_ID)

            # SECRET comes from top-level field
            secret = bytes(user_input.get(CONF_SECRET, b""), "utf-8")

            if url[:8] != "https://":
                errors["base"] = "invalid_path"
            else:
                if username and key_id and secret and plant_id:
                    # Merge nested section keys into _data so CONF_PASSWORD is stored
                    merged = dict(user_input)
                    merged.update(control_section)  # brings CONF_PASSWORD, CONF_CONTROL to top
                    self._data.update(merged)

                    config = SoliscloudConfig(url, username, key_id, secret, plant_id, password)
                    api = SoliscloudAPI(config)
                    if await api.login(async_get_clientsession(self.hass)):
                        await self.async_set_unique_id(plant_id)
                        return self.async_create_entry(title=f"Station {api.plant_name}", data=self._data)
                    errors["base"] = "auth"

        data_schema = {
            vol.Required(CONF_USERNAME, default=None): cv.string,
            vol.Required(CONF_KEY_ID, default=""): cv.string,
            vol.Required(CONF_SECRET, default="00"): cv.string,
            vol.Required(CONF_PLANT_ID, default=None): cv.string,
            vol.Required(CONF_REFRESH_OK, default=300): cv.positive_int,
            vol.Required(CONF_REFRESH_NOK, default=60): cv.positive_int,
            vol.Required("Control"): data_entry_flow.section(
                vol.Schema(
                    {
                        vol.Required(CONF_CONTROL, default=False): bool,
                        vol.Optional(CONF_PASSWORD): cv.string,
                    }
                ),
                {"collapsed": False},
            ),
        }

        return self.async_show_form(
            step_id="credentials_secret",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )


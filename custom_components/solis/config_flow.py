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
    CONF_PORTAL_VERSION,
    CONF_SECRET,
    CONF_USERNAME,
    DEFAULT_DOMAIN,
    DOMAIN,
    SENSOR_PREFIX,
)
from .ginlong_api import GinlongAPI, GinlongConfig
from .soliscloud_api import SoliscloudAPI, SoliscloudConfig

_LOGGER = logging.getLogger(__name__)

PLATFORMV2 = "ginlong_v2"
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
            updated_config = {}
            for key in self.config_entry.data.keys():
                updated_config[key] = self.config_entry.data[key]
            updated_config[CONF_CONTROL] = False
            for key in (CONF_CONTROL, CONF_PASSWORD):
                if key in user_input:
                    updated_config[key] = user_input[key]

            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_config,
                title=user_input.get(CONF_NAME),
            )
        data_schema = {
            vol.Required(CONF_CONTROL, default=False): bool,
            vol.Optional(CONF_PASSWORD, default=""): cv.string,
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
            self._data = user_input
            if user_input.get(CONF_PORTAL_VERSION) is None:
                user_input[CONF_PORTAL_VERSION] = PLATFORMV2
            if user_input.get(CONF_PORTAL_VERSION) == PLATFORMV2:
                return await self.async_step_credentials_password(user_input)
            return await self.async_step_credentials_secret(user_input)

        data_schema = {
            vol.Required(CONF_NAME, default=SENSOR_PREFIX): cv.string,
            vol.Required(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
        }
        data_schema[CONF_PORTAL_VERSION] = selector(
            {
                "select": {
                    "options": [PLATFORMV2, SOLISCLOUD],
                }
            }
        )

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema), errors=errors)

    async def async_step_credentials_password(self, user_input=None):
        """Handle username/password based credential settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = self._data.get(CONF_PORTAL_DOMAIN)
            plant_id = user_input.get(CONF_PLANT_ID)
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            if url[:8] != "https://":
                errors["base"] = "invalid_path"
            else:
                if username and password and plant_id:
                    self._data.update(user_input)
                    config = GinlongConfig(url, username, password, plant_id)
                    api = GinlongAPI(config)
                    if await api.login(async_get_clientsession(self.hass)):
                        await self.async_set_unique_id(plant_id)
                        return self.async_create_entry(title=f"Plant {api.plant_name}", data=self._data)

                    errors["base"] = "auth"

        data_schema = {
            vol.Required(CONF_USERNAME, default=None): cv.string,
            vol.Required(CONF_PASSWORD, default=""): cv.string,
            vol.Required(CONF_PLANT_ID, default=None): cv.positive_int,
        }

        return self.async_show_form(
            step_id="credentials_password",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    async def async_step_credentials_secret(self, user_input=None):
        """Handle key_id/secret based credential settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = self._data.get(CONF_PORTAL_DOMAIN)
            plant_id = user_input.get(CONF_PLANT_ID)
            username = user_input.get(CONF_USERNAME)
            password = user_input.get(CONF_PASSWORD)
            key_id = user_input.get(CONF_KEY_ID)
            secret: bytes = bytes("", "utf-8")
            try:
                secret = bytes(user_input.get(CONF_SECRET), "utf-8")
            except TypeError:
                pass
            if url[:8] != "https://":
                errors["base"] = "invalid_path"
            else:
                if username and key_id and secret and plant_id:
                    self._data.update(user_input)
                    config = SoliscloudConfig(url, username, key_id, secret, plant_id, password)
                    api = SoliscloudAPI(config)
                    if await api.login(async_get_clientsession(self.hass)):
                        await self.async_set_unique_id(plant_id)
                        return self.async_create_entry(title=f"Station {api.plant_name}", data=self._data)

                    errors["base"] = "auth"

        data_schema = {
            vol.Required(CONF_USERNAME, default=None): cv.string,
            vol.Required(CONF_SECRET, default="00"): cv.string,
            vol.Required(CONF_KEY_ID, default=""): cv.string,
            vol.Required(CONF_PLANT_ID, default=None): cv.string,
            vol.Required("Control"): data_entry_flow.section(
                vol.Schema(
                    {
                        vol.Required(CONF_CONTROL, default=False): bool,
                        vol.Optional(CONF_PASSWORD, default=""): cv.string,
                    }
                ),
                # Whether or not the section is initially collapsed (default = False)
                {"collapsed": False},
            ),
        }

        return self.async_show_form(
            step_id="credentials_secret",
            data_schema=vol.Schema(data_schema),
            errors=errors,
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry from configuration.yaml."""

        if user_input is not None:
            if self._async_entry_exists(user_input.get(CONF_PLANT_ID)):
                _str = f"The configuration for plant {user_input.get(CONF_PLANT_ID)} \
                    has already been imported, please remove from configuration.yaml"
                _LOGGER.warning(_str)
                return self.async_abort(reason="already_configured")
            url = user_input.get(CONF_PORTAL_DOMAIN)
            if url[:4] != "http":
                # Fix URL
                url = f"https://{url}"
                user_input[CONF_PORTAL_DOMAIN] = url

            user_input[CONF_PORTAL_VERSION] = PLATFORMV2
            has_key_id = user_input.get(CONF_KEY_ID) != ""
            has_secret: bytes = bytes(user_input.get(CONF_SECRET), "utf-8") != b"\x00"
            if has_key_id and has_secret:
                user_input[CONF_PORTAL_VERSION] = SOLISCLOUD

        return await self.async_step_user(user_input)

    def _async_entry_exists(self, plant_id) -> bool:
        existing_entries = []
        for entry in self._async_current_entries():
            existing_entries.append(entry.data[CONF_PLANT_ID])
        return plant_id in existing_entries

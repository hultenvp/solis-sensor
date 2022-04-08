"""Config flow for Auto Backup integration."""
import logging
import os

import voluptuous as vol
from homeassistant import config_entries
#from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector
from homeassistant.const import (
    CONF_NAME,
)
from .const import (
    DOMAIN,
    CONF_PORTAL_DOMAIN,
    CONF_PORTAL_VERSION,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SECRET,
    CONF_KEY_ID,
    CONF_PLANT_ID,
    SENSOR_PREFIX,
    DEFAULT_DOMAIN,
#    SENSOR_TYPES,
)
from .ginlong_api import GinlongConfig, GinlongAPI
from .soliscloud_api import SoliscloudConfig, SoliscloudAPI

_LOGGER = logging.getLogger(__name__)


def validate_input():
    """Validate existence of Hass.io."""
    for env in ("HASSIO", "HASSIO_TOKEN"):
        if not os.environ.get(env):
            return False
    return True


class SolisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solis."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            if user_input.get(CONF_PORTAL_VERSION) == "ginlong_v2":
                return self.async_step_credentials_password(user_input)
            return self.async_step_credentials_soliscloud(user_input)
        data_schema=vol.Schema(
            {
                vol.Optional(CONF_NAME, default=SENSOR_PREFIX): cv.string,
                vol.Optional(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
            }
        )

        data_schema["platform_generation"] = selector({
            "select": {
                "options": ["ginlong_v2", "soliscloud"],
            }
        })

        return self.async_show_form(step_id="portal", data_schema=vol.Schema(data_schema))

    async def async_step_credentials_password(self, user_input=None):
        """Handle username/password based credential settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url =  user_input.get(CONF_PORTAL_DOMAIN)
            plant_id = user_input.get(CONF_PLANT_ID)
            if url[:8] != 'https://':
                errors["base"] = "invalid_path"
            else:
                config = GinlongConfig(
                    user_input.get(CONF_PORTAL_DOMAIN),
                    user_input.get(CONF_USERNAME),
                    user_input.get(CONF_PASSWORD),
                    user_input.get(CONF_PLANT_ID)
                )
                api = GinlongAPI(config)
                if await api.login(async_get_clientsession(self.hass)):
                    await self.async_set_unique_id(plant_id)
                    return self.async_create_entry(title=f"Station:{plant_id}", data=user_input)

                errors["base"] = "auth"

        data_schema=vol.Schema(
            {
                vol.Required(CONF_USERNAME , default=None): cv.string,
                vol.Required(CONF_PASSWORD , default=''): cv.string,
                vol.Required(CONF_PLANT_ID, default=None): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="password",
            data_schema=vol.Schema(data_schema), errors=errors)

    async def async_step_credentials_soliscloud(self, user_input=None):
        """Handle key_id/secret based credential settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url =  user_input.get(CONF_PORTAL_DOMAIN)
            plant_id = user_input.get(CONF_PLANT_ID)
            if url[:8] != 'https://':
                errors["base"] = "invalid_path"
            else:
                config = SoliscloudConfig(
                    user_input.get(CONF_PORTAL_DOMAIN),
                    user_input.get(CONF_USERNAME),
                    user_input.get(CONF_KEY_ID),
                    user_input.get(CONF_SECRET),
                    plant_id
                )
                api = SoliscloudAPI(config)
                if await api.login(async_get_clientsession(self.hass)):
                    await self.async_set_unique_id(plant_id)
                    return self.async_create_entry(title=f"Station:{plant_id}", data=user_input)

                errors["base"] = "auth"

        data_schema=vol.Schema(
            {
                vol.Required(CONF_USERNAME , default=None): cv.string,
                vol.Required(CONF_SECRET , default='00'): cv.string,
                vol.Required(CONF_KEY_ID , default=''): cv.string,
                vol.Required(CONF_PLANT_ID, default=None): cv.positive_int,
            }
        )

        return self.async_show_form(step_id="secret",
            data_schema=vol.Schema(data_schema), errors=errors)

    async def async_step_import(self, user_input=None):
        """Import a config entry from configuration.yaml."""
        _LOGGER.info("Importing config entry from configuration.yaml")
        url = user_input.get(CONF_PORTAL_DOMAIN)
        if url[:4] != 'http':
            # Fix URL
            url = f"https://{url}"
            user_input[CONF_PORTAL_DOMAIN] = url

        user_input[CONF_PORTAL_VERSION] = "ginlong_v2"
        has_key_id = user_input.get(CONF_KEY_ID) != ''
        has_secret: bytes = bytes(user_input.get(CONF_SECRET), 'utf-8') != b'\x00'
        if has_key_id and has_secret:
            user_input[CONF_PORTAL_VERSION] = "soliscloud"

        return await self.async_step_user(user_input)

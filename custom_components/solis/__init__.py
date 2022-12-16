"""The Solis Inverter integration."""
from datetime import datetime, timedelta, timezone
import asyncio
import logging
import os

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import Platform, ATTR_NAME, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType, HomeAssistantType, ServiceCallType
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    CONF_PORTAL_DOMAIN,
    CONF_PORTAL_VERSION,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SECRET,
    CONF_KEY_ID,
    CONF_PLANT_ID,
)
from .ginlong_base import PortalConfig
from .ginlong_api import GinlongConfig
from .soliscloud_api import SoliscloudConfig
from .service import InverterService

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup(hass: HomeAssistantType, config: ConfigType):
    """Set up the Solis component from configuration.yaml."""

    if "sensor" not in config:
        return True

    for entry in config["sensor"]:
        try:
            if DOMAIN.lower() == entry["platform"]:
                async_create_issue(
                    hass,
                    DOMAIN,
                    "deprecated_yaml",
                    breaks_in_ha_version="2023.2.0",
                    is_fixable=False,
                    severity=IssueSeverity.WARNING,
                    translation_key="deprecated_yaml",
                )
        except TypeError:
            continue
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""

    hass.data.setdefault(DOMAIN, {})

    config = entry.data

    portal_domain = config[CONF_PORTAL_DOMAIN]
    portal_plantid = config[CONF_PLANT_ID]
    portal_username = config[CONF_USERNAME]
    portal_version = config[CONF_PORTAL_VERSION]

    portal_config: PortalConfig | None = None
    if portal_version == "ginlong_v2":
        portal_password = config[CONF_PASSWORD]
        portal_config = GinlongConfig(
            portal_domain, portal_username, portal_password, portal_plantid)
    else:
        portal_key_id = config[CONF_KEY_ID]
        portal_secret: bytes = bytes(config[CONF_SECRET], 'utf-8')
        portal_config = SoliscloudConfig(
            portal_domain, portal_username, portal_key_id, portal_secret, portal_plantid)

    # Initialize the Ginlong data service.
    service: InverterService = InverterService(portal_config, hass)
    hass.data[DOMAIN][entry.entry_id] = service

    # Forward the setup to the sensor platform.
    #hass.async_create_task(
    #    hass.config_entries.async_forward_entry_setup(entry, component)
    #    for component in PLATFORMS
    #)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )

    await hass.data[DOMAIN][entry.entry_id].shutdown()
    return unload_ok

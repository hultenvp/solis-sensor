"""Ginlong data service
Works for m.ginlong.com. Should also work for the myevolvecloud.com portal (not tested)

For more information: https://github.com/hultenvp/solis-sensor/
"""
from __future__ import annotations

import logging

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, final
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

from .ginlong_base import PortalConfig, BaseAPI, GinlongData
from .ginlong_api import GinlongAPI, GinlongConfig
from .soliscloud_api import SoliscloudAPI, SoliscloudConfig
from .ginlong_const import (
    INVERTER_ENERGY_TODAY,
    INVERTER_SERIAL,
    INVERTER_STATE
)

# REFRESH CONSTANTS
SCHEDULE_OK = 2
SCHEDULE_NOK = 1

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '0.2.0'

# Don't login every time
HRS_BETWEEN_LOGIN = timedelta(hours=2)

# Status constants
ONLINE = 'Online'
OFFLINE = 'Offline'

class ServiceSubscriber(ABC):
    """Subscriber base class."""
    def __init__(self) -> None:
        self._measured: datetime | None = None

    @final
    def data_updated(self, value: Any, last_updated: datetime) -> None:
        """Called when service has updates for registered attribute."""
        if self._measured != last_updated:
            if self.do_update(value, last_updated):
                self._measured = last_updated

    @abstractmethod
    def do_update(self, value: Any, last_updated: datetime) -> bool:
        """Implement actual update of attribute."""

class InverterService():
    """Serves all plantId's and inverters on a Ginlong account"""

    def __init__(self, portal_config: PortalConfig, hass: HomeAssistant) -> None:
        self._last_updated: datetime | None = None
        self._logintime: datetime | None = None
        self._subscriptions: dict[str, dict[str, ServiceSubscriber]] = {}
        self._hass: HomeAssistant = hass
        if isinstance(portal_config, GinlongConfig):
            self._api: BaseAPI = GinlongAPI(portal_config)
        elif isinstance(portal_config, SoliscloudConfig):
            self._api = SoliscloudAPI(portal_config)
        else:
            _LOGGER.error("Failed to initialize service, incompatible config")

    async def _login(self) -> bool:
        if not self._api.is_online:
            if await self._api.login(async_get_clientsession(self._hass)):
                self._logintime = datetime.now()
        return self._api.is_online

    async def _logout(self) -> None:
        await self._api.logout()
        self._logintime = None

    async def discover(self) -> dict[str, list[str]]:
        """Discover for all inverters the attributes it supports"""
        capabilities: dict[str, list[str]] = {}
        if await self._login():
            self._logintime = datetime.now()
            inverters = self._api.inverters
            if inverters is None:
                return capabilities
            for inverter_serial in inverters:
                data = await self._api.fetch_inverter_data(inverter_serial)
                if data is not None:
                    capabilities[inverter_serial] = dir(data)
        return capabilities

    def subscribe(self, subscriber: ServiceSubscriber, serial: str, attribute: str
    ) -> None:
        """ Subscribe to changes in 'attribute' from inverter 'serial'."""
        _LOGGER.info("Subscribing sensor to attribute %s for inverter %s",
            attribute, serial)
        if serial not in self._subscriptions:
            self._subscriptions[serial] = {}
        self._subscriptions[serial][attribute] = subscriber

    async def update_devices(self, data: GinlongData) -> None:
        """ Update all registered sensors. """
        serial = getattr(data, INVERTER_SERIAL)
        if serial not in self._subscriptions:
            return
        for attribute in dir(data):
            if attribute in self._subscriptions[serial]:
                value = getattr(data, attribute)
                if attribute == INVERTER_ENERGY_TODAY:
                    # Energy_today is not reset at midnight, but in the morning at
                    # sunrise when the inverter switches back on. This messes up the
                    # energy dashboard. Return 0 while inverter is still off.
                    is_am = datetime.now().hour < 12
                    if getattr(data, INVERTER_STATE) != 1 and is_am:
                        value =  0
                (self._subscriptions[serial][attribute]).data_updated(value, self.last_updated)

    async def async_update(self, *_) -> int:
        """Update the data from Ginlong portal."""
        update = SCHEDULE_NOK
        # Login using username and password, but only every HRS_BETWEEN_LOGIN hours
        if await self._login():
            inverters = self._api.inverters
            if inverters is None:
                return update
            for inverter_serial in inverters:
                data = await self._api.fetch_inverter_data(inverter_serial)
                if data is not None:
                    # And finally get the inverter details
                    update = SCHEDULE_OK
                    self._last_updated = datetime.now()
                    await self.update_devices(data)
                else:
                    update = SCHEDULE_NOK
                    # Reset session and try to login again next time
                    await self._logout()

        await self.schedule_update(update)

        if self._logintime is not None:
            if (self._logintime + HRS_BETWEEN_LOGIN) < (datetime.now()):
                # Time to login again
                await self._logout()

        return update

    async def schedule_update(self, minute: int = 1):
        """ Schedule an update after minute minutes. """
        _LOGGER.debug("Scheduling next update in %s minutes.", minute)
        nxt = dt_util.utcnow() + timedelta(minutes=minute)
        async_track_point_in_utc_time(self._hass, self.async_update, nxt)

    @property
    def status(self):
        """ Return status of service."""
        return ONLINE if self._api.is_online else OFFLINE

    @property
    def last_updated(self):
        """ Return when service last checked for updates."""
        return self._last_updated

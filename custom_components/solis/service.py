"""Ginlong data service
Works for m.ginlong.com. Should also work for the myevolvecloud.com portal (not tested)

For more information: https://github.com/hultenvp/solis-sensor/
"""
from __future__ import annotations

import logging
import time

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
    INVERTER_STATE,
    INVERTER_TIMESTAMP_UPDATE
)

# REFRESH CONSTANTS
# Match up with the default SolisCloud API resolution of 5 minutes
SCHEDULE_OK = 5
# Attempt retries every 1 minute if we fail to talk to the API, though
SCHEDULE_NOK = 1

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '1.0.1'

# Don't login every time
HRS_BETWEEN_LOGIN = timedelta(hours=2)

#Autodiscover
RETRY_DELAY_SECONDS = 60
MAX_RETRY_DELAY_SECONDS = 900

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

    @property
    def measured(self) -> datetime | None:
        """Return timestamp last measurement."""
        return self._measured

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
        self._discovery_callback = None
        self._discovery_cookie: dict[str, Any] = {}
        self._retry_delay_seconds = 0
        if isinstance(portal_config, GinlongConfig):
            self._api: BaseAPI = GinlongAPI(portal_config)
        elif isinstance(portal_config, SoliscloudConfig):
            self._api = SoliscloudAPI(portal_config)
        else:
            _LOGGER.error("Failed to initialize service, incompatible config")
    @property
    def api_name(self) -> str:
        """Return name of the API."""
        return self._api.api_name

    async def _login(self) -> bool:
        if not self._api.is_online:
            if await self._api.login(async_get_clientsession(self._hass)):
                self._logintime = datetime.now()
        return self._api.is_online

    async def _logout(self) -> None:
        await self._api.logout()
        self._logintime = None

    async def async_discover(self, *_) -> None:
        """ Try to discover and retry if needed."""
        capabilities: dict[str, list[str]] = {}
        capabilities = await self._do_discover()
        if capabilities:
            if self._discovery_callback and self._discovery_cookie:
                self._discovery_callback(capabilities, self._discovery_cookie)
            self._retry_delay_seconds = 0
        else:
            self._retry_delay_seconds = min(MAX_RETRY_DELAY_SECONDS, \
                self._retry_delay_seconds + RETRY_DELAY_SECONDS)
            _LOGGER.warning("Failed to discover, scheduling retry in %s seconds.", \
                self._retry_delay_seconds)
            await self._logout()
            self.schedule_discovery(self._discovery_callback, self._discovery_cookie, \
                self._retry_delay_seconds)

    async def _do_discover(self) -> dict[str, list[str]]:
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
                    capabilities[inverter_serial] = data.keys()
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
        try:
            serial = getattr(data, INVERTER_SERIAL)
        except AttributeError:
            return
        if serial not in self._subscriptions:
            return
        for attribute in data.keys():
            if attribute in self._subscriptions[serial]:
                value = getattr(data, attribute)
                if attribute == INVERTER_ENERGY_TODAY:
                    # Energy_today is not reset at midnight, but in the morning at
                    # sunrise when the inverter switches back on. This messes up the
                    # energy dashboard. Return 0 while inverter is still off.
                    is_am = datetime.now().hour < 12
                    if getattr(data, INVERTER_STATE) == 2 and is_am:
                        value = 0
                    elif getattr(data, INVERTER_STATE) == 1 and is_am:
                        last_updated_state = None
                        try:
                            last_updated_state = \
                                self._subscriptions[serial][INVERTER_STATE].measured
                        except KeyError:
                            pass
                        if last_updated_state is not None:
                            # Hybrid systems do not reset in the morning, but just after midnight.
                            if last_updated_state.hour == 0 and last_updated_state.minute < 15:
                                value = 0
                            # Avoid race conditions when between state change in the morning and
                            # energy today being reset by adding 5 min grace period and
                            # skipping update
                            elif last_updated_state + timedelta(minutes=5) > datetime.now():
                                continue
                (self._subscriptions[serial][attribute]).data_updated(value, self.last_updated)

    async def async_update(self, *_) -> None:
        """Update the data from Ginlong portal."""
        update = timedelta(minutes=SCHEDULE_NOK)
        # Login using username and password, but only every HRS_BETWEEN_LOGIN hours
        if await self._login():
            inverters = self._api.inverters
            if inverters is None:
                return
            for inverter_serial in inverters:
                data = await self._api.fetch_inverter_data(inverter_serial)
                if data is not None:
                    # And finally get the inverter details
                    # default to updating after SCHEDULE_OK minutes;
                    update = timedelta(minutes=SCHEDULE_OK)
                    # ...but try to figure out a better next-update time based on when the API last received its data
                    try:
                        ts = getattr(data, INVERTER_TIMESTAMP_UPDATE)
                        nxt = dt_util.utc_from_timestamp(ts) + update + timedelta(seconds=1)
                        if nxt > dt_util.utcnow():
                            update = nxt - dt_util.utcnow()
                    except AttributeError:
                        pass # no last_update found, so keep just using SCHEDULE_OK as a safe default
                    self._last_updated = datetime.now()
                    await self.update_devices(data)
                else:
                    update = timedelta(minutes=SCHEDULE_NOK)
                    # Reset session and try to login again next time
                    await self._logout()

        self.schedule_update(update)

        if self._logintime is not None:
            if (self._logintime + HRS_BETWEEN_LOGIN) < (datetime.now()):
                # Time to login again
                await self._logout()

    def schedule_update(self, td: timedelta) -> None:
        """ Schedule an update after td time. """
        nxt = dt_util.utcnow() + td
        _LOGGER.debug("Scheduling next update in %s, at %s", str(td), nxt)
        async_track_point_in_utc_time(self._hass, self.async_update, nxt)

    def schedule_discovery(self, callback, cookie: dict[str, Any], seconds: int = 1):
        """ Schedule a discovery after seconds seconds. """
        _LOGGER.debug("Scheduling discovery in %s seconds.", seconds)
        self._discovery_callback = callback
        self._discovery_cookie = cookie
        nxt = dt_util.utcnow() + timedelta(seconds=seconds)
        async_track_point_in_utc_time(self._hass, self.async_discover, nxt)

    async def shutdown(self):
        """ Shutdown the service """
        await self._logout()

    @property
    def status(self):
        """ Return status of service."""
        return ONLINE if self._api.is_online else OFFLINE

    @property
    def last_updated(self):
        """ Return when service last checked for updates."""
        return self._last_updated

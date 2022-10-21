"""Ginlong base classes
For more information: https://github.com/hultenvp/solis-sensor/
"""
from __future__ import annotations

import logging

from abc import ABC, abstractmethod
#from typing import final
from aiohttp import ClientSession

from .ginlong_const import INVERTER_STATE

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '0.1.1'

class PortalConfig(ABC):
    """ Portal configuration data """

    def __init__(self,
        portal_domain: str,
        portal_username: str,
        portal_plant_id: str
    ) -> None:
        self._domain: str = portal_domain
        self._username: str = portal_username
        self._plant_id: str = portal_plant_id

    @property
    def domain(self) -> str:
        """ Configured portal domain name."""
        return self._domain

    @property
    def username(self) -> str:
        """ Username."""
        return self._username

    @property
    def plant_id(self) -> str:
        """ Configured plant ID."""
        return self._plant_id

class GinlongData():
    """ Representing data measurement for one inverter from Ginlong API """

    def __init__(self, data: dict[str, str | int | float]) -> None:
        """ Initialize the data object """
        self._data = dict(data)


    def get_inverter_data(self) -> dict[str, str | int | float]:
        """Return all available measurements in a dict."""
        return self._data

    def keys(self) -> list[str]:
        """Return keys of all measurements in a list, ensure state is first."""
        available_measurements: list[str] = list(self._data.keys())
        # Move state to beginning of list to avoid race conditions for the
        # energy today fix.
        available_measurements.remove(INVERTER_STATE)
        available_measurements.insert(0, INVERTER_STATE)
        return available_measurements

    def __getattr__(self, name):
        """Each measurement is represented as property."""
        try:
            return self._data[name]
        except KeyError as key_error:
            _LOGGER.debug("AttributeError, %s does not exist", name)
            raise AttributeError(name) from key_error

class BaseAPI(ABC):
    """ API Base class."""
    def __init__(self, config: PortalConfig) -> None:
        self._config: PortalConfig = config
        self._session: ClientSession | None = None
        self._inverter_list: dict[str, str] | None = None
        self._plant_name: str | None = None

    @property
    def config(self) -> PortalConfig:
        """ Config this for this API instance."""
        return self._config

    @property
    def inverters(self) -> dict[str, str] | None:
        """ Return the list of inverters for plant ID when logged in."""
        return self._inverter_list

    @property
    def plant_name(self) -> str | None:
        """ Return plant name for this API instance."""
        return self._plant_name

    @property
    def plant_id(self) -> str | None:
        """ Return plant ID for this API instance."""
        return self._config.plant_id

    @property
    @abstractmethod
    def api_name(self) -> str:
        """ Return name of the API."""

    @property
    @abstractmethod
    def is_online(self) -> bool:
        """ Returns if we are logged in."""

    @abstractmethod
    async def login(self, session: ClientSession) -> bool:
        """ Login to service."""

    @abstractmethod
    async def logout(self) -> None:
        """ Close session."""

    @abstractmethod
    async def fetch_inverter_list(self, plant_id: str) -> dict[str, str]:
        """ Retrieve inverter list from service."""

    @abstractmethod
    async def fetch_inverter_data(self, inverter_serial: str) -> GinlongData | None:
        """
        Fetch data for given inverter. Collect available data from payload and store
        as GinlongData object.
        """

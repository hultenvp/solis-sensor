"""
Solis Solar interface for Home Assistant
This component offers Solis portal data as a sensor.

For more information: https://github.com/hultenvp/solis-sensor/
"""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any
import voluptuous as vol

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import (
    CONF_NAME,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from .const import (
    CONF_PORTAL_DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_SECRET,
    CONF_KEY_ID,
    CONF_PLANT_ID,
    SENSOR_PREFIX,
    DEFAULT_DOMAIN,
    SENSOR_TYPES,
)

from .service import (ServiceSubscriber, InverterService)
from .ginlong_base import PortalConfig
from .ginlong_api import GinlongConfig
from .soliscloud_api import SoliscloudConfig

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '2.3.3'

LAST_UPDATED = 'Last updated'
SERIAL = 'Inverter serial'

EMPTY_ATTR: dict[str, Any] = {
    LAST_UPDATED: None,
    SERIAL: None,
}

def _check_config_schema(config: ConfigType):
    # Check input configuration.
    portal_domain = config.get(CONF_PORTAL_DOMAIN)
    if portal_domain is None:
        raise vol.Invalid('configuration parameter [portal_domain] does not have a value')
    elif portal_domain[:4] == 'http':
        raise vol.Invalid('leave http(s):// out of configuration parameter [portal_domain]')
    if config.get(CONF_USERNAME) is None:
        raise vol.Invalid('configuration parameter [portal_username] does not have a value')
    if config.get(CONF_PLANT_ID) is None:
        raise vol.Invalid('Configuration parameter [portal_plantid] does not have a value')
    has_password = config.get(CONF_PASSWORD) != ''
    has_key_id = config.get(CONF_KEY_ID) != ''
    has_secret: bytes = bytes(config.get(CONF_SECRET), 'utf-8') != b'\x00'
    if not (has_password ^ (has_key_id and has_secret)):
        raise vol.Invalid('Please specify either[portal_password] or [portal_key_id] & [portal_secret]')

    return config

PLATFORM_SCHEMA = vol.All(PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=SENSOR_PREFIX): cv.string,
    vol.Optional(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
    vol.Required(CONF_USERNAME , default=None): cv.string,
    vol.Optional(CONF_PASSWORD , default=''): cv.string,
    vol.Optional(CONF_SECRET , default='00'): cv.string,
    vol.Optional(CONF_KEY_ID , default=''): cv.string,
    vol.Required(CONF_PLANT_ID, default=None): cv.positive_int,
}, extra=vol.PREVENT_EXTRA), _check_config_schema)

def create_sensors(sensors: dict[str, list[str]],
        inverter_service: InverterService,
        inverter_name: str
    ) -> list[SolisSensor]:
    """ Create the sensors."""
    hass_sensors = []
    for inverter_sn in sensors:
        for sensor_type in sensors[inverter_sn]:
            _LOGGER.debug("Creating %s (%s)", sensor_type, inverter_sn)
            hass_sensors.append(SolisSensor(inverter_service, inverter_name,
                inverter_sn, sensor_type))
    return hass_sensors

async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        async_add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None) -> None:
    """Set up Solis platform."""

    inverter_name = config.get(CONF_NAME)
    portal_domain = config.get(CONF_PORTAL_DOMAIN)
    portal_username = config.get(CONF_USERNAME)
    portal_password = config.get(CONF_PASSWORD)
    portal_key_id = config.get(CONF_KEY_ID)
    portal_secret: bytes = bytes(config.get(CONF_SECRET), 'utf-8')
    portal_plantid = config.get(CONF_PLANT_ID)

    portal_config: PortalConfig | None = None
    if portal_password != '':
        portal_config = GinlongConfig(
            portal_domain, portal_username, portal_password, portal_plantid)
    elif portal_key_id != '' and portal_secret != b'\x00':
        portal_config = SoliscloudConfig(
            portal_domain, portal_username, portal_key_id, portal_secret, portal_plantid)
    else:
        raise vol.Invalid('Please specify either[portal_password] or [portal_key_id] & [portal_secret]')

    # Initialize the Ginlong data service.
    service: InverterService = InverterService(portal_config, hass)

    # Prepare the sensor entities.
    hass_sensors: list[SolisSensor] = []

    cookie: dict[str, Any] = {
        'name': inverter_name,
        'service': service,
        'async_add_entities' : async_add_entities
    }
    # Will retry endlessly to discover
    _LOGGER.info("Scheduling discovery")
    service.schedule_discovery(on_discovered, cookie, 1)

@callback
def on_discovered(capabilities, cookie):
    """ Callback when discovery was successful."""
    discovered_sensors: dict[str, list]= {}
    for inverter_sn in capabilities:
        for sensor in SENSOR_TYPES.keys():
            if SENSOR_TYPES[sensor][5] in capabilities[inverter_sn]:
                if inverter_sn not in discovered_sensors:
                    discovered_sensors[inverter_sn] = list()
                discovered_sensors[inverter_sn].append(sensor)
    if not discovered_sensors:
        _LOGGER.warning("No sensors detected, nothing to register")

    # Create the sensors
    hass_sensors = create_sensors(discovered_sensors, cookie['service'], cookie['name'])
    cookie['async_add_entities'](hass_sensors)
    # schedule the first update in 1 minute from now:
    cookie['service'].schedule_update(1)

class SolisSensor(ServiceSubscriber, SensorEntity):
    """ Representation of a Solis sensor. """

    def __init__(self,
            ginlong_service: InverterService,
            inverter_name: str,
            inverter_sn: str,
            sensor_type: str
        ):
        # Initialize the sensor.
        self._measured: datetime | None = None
        self._attributes = EMPTY_ATTR
        self._attributes[SERIAL] = inverter_sn
        # Properties
        self._icon = SENSOR_TYPES[sensor_type][2]
        self._name = inverter_name + ' ' + SENSOR_TYPES[sensor_type][0]
        self._attr_native_value = None
        self._attr_native_unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self._attr_device_class = SENSOR_TYPES[sensor_type][3]
        self._attr_state_class = SENSOR_TYPES[sensor_type][4]
        self._attr_unique_id = f"{inverter_sn}{self._name}".replace(" ", "_")
        ginlong_service.subscribe(self, inverter_sn, SENSOR_TYPES[sensor_type][5])

    def do_update(self, value: Any, last_updated: datetime) -> bool:
        """ Update the sensor."""
        if self.hass and self._attr_native_value != value:
            self._attr_native_value = value
            self._attributes[LAST_UPDATED] = last_updated
            self.async_write_ha_state()
            return True
        return False

    @property
    def icon(self):
        """ Return the icon of the sensor. """
        return self._icon

    @property
    def name(self):
        """ Return the name of the sensor. """
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes

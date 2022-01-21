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

from homeassistant.core import HomeAssistant
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
    CONF_INVERTER_SERIAL,
    CONF_SENSORS,
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
VERSION = '1.0.0'

LAST_UPDATED = 'Last updated'
SERIAL = 'Inverter serial'

EMPTY_ATTR: dict[str, Any] = {
    LAST_UPDATED: None,
    SERIAL: None,
}

def _check_config_schema(conf: ConfigType):
    """Check if the sensors and attributes are valid."""
    if CONF_SENSORS in conf.keys():
        _LOGGER.warning("Deprecated platform configuration, please move to the new configuration")
        if conf[CONF_INVERTER_SERIAL] == '':
            raise vol.Invalid('inverter_serial required in config when sensors are specified')

        for sensor, attrs in conf[CONF_SENSORS].items():
            if sensor not in SENSOR_TYPES:
                raise vol.Invalid('sensor {} does not exist'.format(sensor))
            for attr in attrs:
                if attr not in SENSOR_TYPES:
                    raise vol.Invalid('attribute sensor {} does not \
                        exist [{}]'.format(attr, sensor))
    else:
        if conf[CONF_INVERTER_SERIAL] != '':
            _LOGGER.warning("Using new config schema, ignoring inverter_serial")
    return conf

PLATFORM_SCHEMA = vol.All(PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=SENSOR_PREFIX): cv.string,
    vol.Optional(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
    vol.Required(CONF_USERNAME , default=None): cv.string,
    vol.Optional(CONF_PASSWORD , default=''): cv.string,
    vol.Optional(CONF_SECRET , default=''): cv.string,
    vol.Optional(CONF_KEY_ID , default=''): cv.string,
    vol.Required(CONF_PLANT_ID, default=None): cv.positive_int,
    vol.Optional(CONF_INVERTER_SERIAL, default=''): cv.string,
    vol.Optional(CONF_SENSORS): vol.Schema({cv.slug: cv.ensure_list}),
}, extra=vol.PREVENT_EXTRA), _check_config_schema)

async def async_autodetect(inverter_service: InverterService) -> dict[str, list[str]]:
    """ Autodetect capabilities per inverter."""
    capabilities = await inverter_service.discover()
    _LOGGER.debug("%s", capabilities)
    # Build list of sensors for each inverter
    discovered_sensors: dict[str, list]= {}
    for inverter_sn in capabilities:
        for sensor in SENSOR_TYPES.keys():
            if SENSOR_TYPES[sensor][5] in capabilities[inverter_sn]:
                if inverter_sn not in discovered_sensors:
                    discovered_sensors[inverter_sn] = list()
                discovered_sensors[inverter_sn].append(sensor)

    return discovered_sensors

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

def create_sensors_legacy(
        config: ConfigType,
        inverter_service: InverterService,
        inverter_name: str,
        inverter_sn: str
    ) -> list[SolisSensor]:
    """Legacy for old config schema."""
    hass_sensors = []
    for sensor_type, subtypes in config[CONF_SENSORS].items():
        _LOGGER.debug("Creating %s sensor: %s", inverter_name, sensor_type)
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
    portal_secret = config.get(CONF_SECRET)
    portal_plantid = config.get(CONF_PLANT_ID)
    inverter_sn = config.get(CONF_INVERTER_SERIAL)

    # Check input configuration.
    if portal_domain is None:
        raise vol.Invalid('configuration parameter [portal_domain] does not have a value')
    if portal_domain[:4] == 'http':
        raise vol.Invalid('leave http(s):// out of configuration parameter [portal_domain]')
    if portal_username is None:
        raise vol.Invalid('configuration parameter [portal_username] does not have a value')
    portal_config: PortalConfig | None = None
    if portal_password != '':
        portal_config = GinlongConfig(
            portal_domain, portal_username, portal_password, portal_plantid)
    elif portal_key_id != '' and portal_secret != '':
        portal_config = SoliscloudConfig(
            portal_domain, portal_username, portal_secret, portal_key_id, portal_plantid)
    else:
        raise vol.Invalid('please specify either[portal_password] or [portal_key_id] & [portal_secret]')
    if portal_plantid is None:
        raise vol.Invalid('configuration parameter [portal_plantid] does not have a value')

    # Initialize the Ginlong data service.
    service: InverterService = InverterService(portal_config, hass)

    # Prepare the sensor entities.
    hass_sensors: list[SolisSensor] = []

    if CONF_SENSORS in config.keys():
        # Old config schema
        hass_sensors = create_sensors_legacy(config, service, inverter_name, inverter_sn)
    else:
        sensors = await async_autodetect(service)
        # Create the sensors
        hass_sensors = create_sensors(sensors, service, inverter_name)
    async_add_entities(hass_sensors)

    # schedule the first update in 1 minute from now:
    await service.schedule_update(1)

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
        if self.hass:
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

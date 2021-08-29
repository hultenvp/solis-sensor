"""
  Solis Solar interface for Home Assistant.
  This component offers Solis portal data as a sensor.

  For more information: https://github.com/hultenvp/solis-sensor/
"""
import binascii
import hashlib
import homeassistant.helpers.config_validation as cv
import logging
import struct
import sys
import voluptuous as vol

from datetime import datetime
from datetime import timedelta
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
)
from homeassistant.const import ( 
    EVENT_HOMEASSISTANT_STOP, 
    CONF_NAME, 
    CONF_SCAN_INTERVAL, 
    TEMP_CELSIUS,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_TEMPERATURE,)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity


from .platform2_portal import InverterData as inverter
from .platform2_portal import PortalConfig as inverter_config

# VERSION
VERSION = '0.2.0'

_LOGGER = logging.getLogger(__name__)

CONF_PORTAL_DOMAIN = 'portal_domain'
CONF_USERNAME = 'portal_username'
CONF_PASSWORD = 'portal_password'
CONF_PLANT_ID = 'portal_plant_id'
CONF_INVERTER_SERIAL = 'inverter_serial'
CONF_SENSORS = 'sensors'

SENSOR_PREFIX = 'Solis'
DEFAULT_DOMAIN = 'm.ginlong.com'

# Supported sensor types:
# Key: ['label', unit, icon, device class, state class]
SENSOR_TYPES = {
    'status':            ['Status', None, 'mdi:solar-power', None, None],
    'temperature':       ['Temperature', TEMP_CELSIUS, 'mdi:thermometer', DEVICE_CLASS_TEMPERATURE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv1': ['DC Voltage PV1', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv2': ['DC Voltage PV2', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv3': ['DC Voltage PV3', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv4': ['DC Voltage PV4', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv1': ['DC Current PV1', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv2': ['DC Current PV2', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv3': ['DC Current PV3', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv4': ['DC Current PV4', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage1':  ['AC Voltage R', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage2':  ['AC Voltage S', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage3':  ['AC Voltage T', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent1':  ['AC Current R', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent2':  ['AC Current S', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent3':  ['AC Current T', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'actualpower':       ['AC Output Total Power', 'W', 'mdi:weather-sunny', DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT], 
    'energylastmonth':   ['Energy Last Month', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energytoday':       ['Energy Today', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energythismonth':   ['Energy This Month', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energythisyear':    ['energy This Year', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energytotal':       ['Energy Total', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING]
}

def _check_config_schema(conf):
  """ Check if the sensors and attributes are valid. """

  for sensor, attrs in conf[CONF_SENSORS].items():
    if(sensor not in SENSOR_TYPES):
      raise vol.Invalid('sensor {} does not exist'.format(sensor))
    for attr in attrs:
      if(attr not in SENSOR_TYPES):
        raise vol.Invalid('attribute sensor {} does not exist [{}]'.format(attr, sensor))

  return conf

PLATFORM_SCHEMA = vol.All(PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=SENSOR_PREFIX): cv.string,
    vol.Optional(CONF_PORTAL_DOMAIN, default=DEFAULT_DOMAIN): cv.string,
    vol.Optional(CONF_USERNAME , default=None): cv.string,
    vol.Optional(CONF_PASSWORD , default=None): cv.string,
    vol.Optional(CONF_PLANT_ID, default=None): cv.positive_int,
    vol.Optional(CONF_INVERTER_SERIAL, default=None): cv.string,
    vol.Required(CONF_SENSORS): vol.Schema({cv.slug: cv.ensure_list}),
}, extra=vol.PREVENT_EXTRA), _check_config_schema)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
  """ Set up Solis sensor. """

  inverter_name = config.get(CONF_NAME)
  portal_domain = config.get(CONF_PORTAL_DOMAIN)
  portal_username = config.get(CONF_USERNAME)
  portal_password = config.get(CONF_PASSWORD)
  portal_plantid = config.get(CONF_PLANT_ID)
  inverter_sn = config.get(CONF_INVERTER_SERIAL)

  # Check input configuration.
  if(portal_domain == None):
    raise vol.Invalid('configuration parameter [portal_domain] does not have a value')
  if(portal_domain[:4] == 'http'):
    raise vol.Invalid('leave http(s):// out of configuration parameter [portal_domain]')
  if(portal_username == None):
    raise vol.Invalid('configuration parameter [portal_username] does not have a value')
  if(portal_password == None):
    raise vol.Invalid('configuration parameter [portal_password] does not have a value')
  if(portal_plantid == None):
    raise vol.Invalid('configuration parameter [portal_plantid] does not have a value')
  if(inverter_sn == None):
    raise vol.Invalid('configuration parameter [inverter_serial] does not have a value')

  # Determine for which sensors data should be retrieved.
  used_sensors = []
  for sensor_type in config[CONF_SENSORS].items():
    used_sensors.append(sensor_type)

  # Prepare the sensor entities.
  hass_sensors = []
  for sensor_type, subtypes in config[CONF_SENSORS].items():
    _LOGGER.debug("Creating solis sensor: %s", sensor_type)
    hass_sensors.append(SolisSensor(inverter_name, sensor_type))

  async_add_entities(hass_sensors)
  # schedule the first update in 1 minute from now:
  _LOGGER.debug("Starting updates....")

  # Initialize the Solis data interface.
  portal_config = inverter_config(portal_domain, portal_username, portal_password, portal_plantid, inverter_sn)
  data = inverter(portal_config, hass, hass_sensors)

  await data.schedule_update(1)

class SolisSensor(Entity):
  """ Representation of a Solis sensor. """

  def __init__(self, inverter_name, sensor_type):
    # Initialize the sensor.
    self._inverter_name = inverter_name
    self._type = sensor_type
    self._measured = None
    # Properties
    self._icon = SENSOR_TYPES[sensor_type][2]
    self._name = self._inverter_name + ' ' + SENSOR_TYPES[sensor_type][0]
    self._state = None
    self._uom = SENSOR_TYPES[sensor_type][1]
    self._device_class = SENSOR_TYPES[sensor_type][3]
    self._state_class = SENSOR_TYPES[sensor_type][4]

  @callback
  def data_updated(self, data):
    """Update data."""
    if self._load_data(data) and self.hass:
      self.async_write_ha_state()

  @callback
  def _load_data(self, data):
    """Load the sensor with relevant data."""
    # Find sensor

    # Check if we have a new measurement,
    # otherwise we do not have to update the sensor
    if self._measured == data.last_updated:
      return False

    # Property name in data interface must be equal to sensor type
    self._state = getattr(data, self._type)
    self._measured = data.last_updated
    return True

  @property
  def icon(self):
    """ Return the icon of the sensor. """
    return self._icon

  @property
  def name(self):
    """ Return the name of the sensor. """
    return self._name

  @property
  def unit_of_measurement(self):
    """ Return the unit the value is expressed in. """
    uom = self._uom
    if(self._state is None):
      uom = None
    return uom

  @property
  def device_class
    """ Return device class """
    return self._device_class
  
  @property
  def state_class
    """ Return state class
    return self._state_class
    
  @property
  def state(self):
    """ Return the state of the sensor. """
    return self._state

  @property
  def should_poll(self):
    """No polling needed."""
    return False


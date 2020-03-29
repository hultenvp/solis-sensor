"""
  Solis Solar interface.
  Inspired by Omnik Solar interface https://github.com/heinoldenhuis/home_assistant_omnik_solar/
  This component offers Solis portal data as a sensor.
  
  For more information: https://github.com/hultenvp/solis-sensor/
"""

import logging
from datetime import datetime
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ( EVENT_HOMEASSISTANT_STOP, CONF_NAME, CONF_SCAN_INTERVAL )
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from urllib.request import urlopen
from xml.etree import ElementTree as etree

import binascii
import hashlib
import struct
import sys
import requests

# VERSION
VERSION = '0.0.4'

BASE_URL = 'http://{0}:{1}{2}'

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)
HRS_BETWEEN_LOGIN = timedelta(hours=12)

DEFAULT_DOMAIN = 'm.ginlong.com'
# Don't login every time

CONF_PORTAL_DOMAIN = 'portal_domain'
CONF_USERNAME = 'portal_username'
CONF_PASSWORD = 'portal_password'
CONF_PLANT_ID = 'portal_plant_id'
CONF_INVERTER_SERIAL = 'inverter_serial'
CONF_SENSORS = 'sensors'

SENSOR_PREFIX = 'Solis'
SENSOR_TYPES = {
    'status':            ['Status', None, 'mdi:solar-power'],
    'temperature':       ['Temperature', '°C', 'mdi:thermometer'],
    'dcinputvoltagepv1': ['DC Voltage PV1', 'V', 'mdi:flash-outline'],
    'dcinputvoltagepv2': ['DC Voltage PV2', 'V', 'mdi:flash-outline'],
    'dcinputvoltagepv3': ['DC Voltage PV3', 'V', 'mdi:flash-outline'],
    'dcinputvoltagepv4': ['DC Voltage PV4', 'V', 'mdi:flash-outline'],
    'dcinputcurrentpv1': ['DC Current 1', 'A', 'mdi:flash-outline'],
    'dcinputcurrentpv2': ['DC Current 2', 'A', 'mdi:flash-outline'],
    'dcinputcurrentpv3': ['DC Current 3', 'A', 'mdi:flash-outline'],
    'dcinputcurrentpv4': ['DC Current 4', 'A', 'mdi:flash-outline'],
    'acoutputvoltage1':  ['AC Voltage R', 'V', 'mdi:flash-outline'],
    'acoutputvoltage2':  ['AC Voltage S', 'V', 'mdi:flash-outline'],
    'acoutputvoltage3':  ['AC Voltage T', 'V', 'mdi:flash-outline'],
    'acoutputcurrent1':  ['AC Current R', 'A', 'mdi:flash-outline'],
    'acoutputcurrent2':  ['AC Current S', 'A', 'mdi:flash-outline'],
    'acoutputcurrent3':  ['AC Current T', 'A', 'mdi:flash-outline'],
    'actualpower':       ['AC Output Total Power', 'W', 'mdi:weather-sunny'], 
    'energylastmonth':   ['Energy Last Month', 'kWh', 'mdi:flash-outline'],
    'energytoday':       ['Energy Today', 'kWh', 'mdi:flash-outline'],
    'energythismonth':   ['Energy This Month', 'kWh', 'mdi:flash-outline'],
    'energythisyear':    ['energy This Year', 'kWh', 'mdi:flash-outline'],
    'energytotal':       ['Energy Total', 'kWh', 'mdi:flash-outline'],
#    'dcinputpowerpv1':   ['DC Power PV1', 'W', 'mdi:flash-outline'],
#    'dcinputpowerpv2':   ['DC Power PV2', 'W', 'mdi:flash-outline'],
#    'dcinputpowerpv3':   ['DC Power PV3', 'W', 'mdi:flash-outline'],
#    'dcinputpowerpv4':   ['DC Power PV4', 'W', 'mdi:flash-outline']
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

def setup_platform(hass, config, add_devices, discovery_info=None):
  """ Set up Solis sensor. """
  inverter_name = config.get(CONF_NAME)
  portal_domain = config.get(CONF_PORTAL_DOMAIN)
  portal_username = config.get(CONF_USERNAME)
  portal_password = config.get(CONF_PASSWORD)
  portal_plantid = config.get(CONF_PLANT_ID)
  inverter_sn = config.get(CONF_INVERTER_SERIAL)
  
  """ Check input configuration. """
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
  
  """ Determine for which sensors data should be retrieved. """
  used_sensors = []
  for type, subtypes in config[CONF_SENSORS].items():
    used_sensors.append(type)
    used_sensors.extend(subtypes)
    
  """ Initialize the Solis data interface. """
  data = SolisData(portal_domain, portal_username, portal_password, portal_plantid, inverter_sn, used_sensors)
  
  """ Prepare the sensor entities. """
  hass_sensors = []
  for type, subtypes in config[CONF_SENSORS].items():
    hass_sensors.append(SolisSensor(inverter_name, data, type, subtypes))
  
  add_devices(hass_sensors)

class SolisSensor(Entity):
  """ Representation of a Solis sensor. """
  
  def __init__(self, inverter_name, data, type, subtypes):
    """Initialize the sensor."""
    self._inverter_name = inverter_name
    self._data = data
    self._type = type
    self._subtypes = subtypes
    self.p_icon = SENSOR_TYPES[self._type][2]
    self.p_name = self._inverter_name + ' ' + SENSOR_TYPES[self._type][0]
    self.p_state = None
    self.p_subtypes = {SENSOR_TYPES[subtype][0]: '{}'.format('unknown') for subtype in subtypes}
    self.p_uom = SENSOR_TYPES[self._type][1]
  
  @property
  def device_state_attributes(self):
    """ Return the state attributes of the sensor. """
    return self.p_subtypes
  
  @property
  def icon(self):
    """ Return the icon of the sensor. """
    return self.p_icon
    
  @property
  def name(self):
    """ Return the name of the sensor. """
    return self.p_name
  
  @property
  def unit_of_measurement(self):
    """ Return the unit the value is expressed in. """
    uom = self.p_uom
    if(self.p_state is None):
      uom = None
    return uom
  
  @property
  def state(self):
    """ Return the state of the sensor. """
    return self.p_state
  
  def update(self):
    """ Update this sensor using the data. """
    
    """ Get the latest data and use it to update our sensor state. """
    self._data.update()
    
    """ Retrieve the sensor data from Solis Data. """
    sensor_data = self._data.get_sensor_data()
    
    """ Update attribute sensor values. """
    for subtype in self._subtypes:
      newval = sensor_data[subtype]
      uom = SENSOR_TYPES[subtype][1]
      if(uom is None):
        subtypeval = '{}'.format(newval)
      else:
        subtypeval = '{} {}'.format(newval, uom)
        
      self.p_subtypes[SENSOR_TYPES[subtype][0]] = subtypeval
    
    """ Update sensor value. """
    new_state = sensor_data[self._type]
    self.p_state = new_state

class SolisData(object):
  """ Representation of a Solis data object used for retrieving data values. """

  def __init__(self, portal_domain, portal_username, portal_password, portal_plantid, inverter_sn, sensors):
    """ Initialize Solis data component. """
    self._portal_domain = portal_domain
    self._portal_username = portal_username
    self._portal_password = portal_password
    self._portal_plantid = portal_plantid
    self._inverter_sn = inverter_sn
    self._sensors = sensors
    self.interface_portal = SolisPortal(self._portal_domain, self._portal_username, self._portal_password, self._portal_plantid, self._inverter_sn)
    self.sensor_data = {type: None for type in list(self._sensors)}
  
  def get_sensor_data(self):
    """ Return an array with the sensors and their values. """
    return self.sensor_data
  
  def get_statistics(self):
    """ Gets the statistics from the portal. """
    self.interface_portal.get_statistics()
  
  def decode_data(self, data, sensor_type):
    """ Gets the data values from the sensors. """
    value = None
  
    """ Retrieve value. """
    if(sensor_type == 'status'):
      if(self.interface_portal.is_online()):
        value = 'Online'
      else:
        value = 'Offline'
        #_LOGGER.warn('read_sensor: inverter enabled %s', inverter_enabled)
    elif(sensor_type == 'temperature'):
      # Temp is a decimal value
      value = float(data.get('1df'))
    elif(sensor_type == 'dcinputvoltagepv1'):
      # DC voltage of PV string 1
      value = float(data.get('1a'))
    elif(sensor_type == 'dcinputvoltagepv2'):
      # DC voltage of PV string 2
      value = float(data.get('1b'))
    elif(sensor_type == 'dcinputvoltagepv3'):
      # DC voltage of PV string 3
      value = float(data.get('1c'))
    elif(sensor_type == 'dcinputvoltagepv4'):
      # DC voltage of PV string 4
      value = float(data.get('1d'))
    elif(sensor_type == 'dcinputcurrentpv1'):
      # DC current of PV string 1
      value = float(data.get('1j'))
    elif(sensor_type == 'dcinputcurrentpv2'):
      # DC current of PV string 2
      value = float(data.get('1k'))
    elif(sensor_type == 'dcinputcurrentpv3'):
      # DC current of PV string 3
      value = float(data.get('1l'))
    elif(sensor_type == 'dcinputcurrentpv4'):
      # DC current of PV string 4
      value = float(data.get('1m'))
#    elif(sensor_type == 'dcinputpowerpv1'):
      # DC power of PV string 1
#      value = float(data.get('1s'))
#    elif(sensor_type == 'dcinputpowerpv2'):
      # DC power of PV string 2
#      value = float(data.get('1t'))
#    elif(sensor_type == 'dcinputpowerpv3'):
      # DC power of PV string 3
#      value = float(data.get('1u'))
#    elif(sensor_type == 'dcinputpowerpv4'):
      # DC power of PV string 4
#      value = float(data.get('1v'))
    elif(sensor_type == 'acoutputvoltage1'):
      # AC output voltage of 1st phase 
      value = float(data.get('1af'))
    elif(sensor_type == 'acoutputvoltage2'):
      # AC output voltage of 2nd phase 
      value = float(data.get('1ag'))
    elif(sensor_type == 'acoutputvoltage3'):
      # AC output voltage of 3rd phase 
      value = float(data.get('1ah'))
    elif(sensor_type == 'acoutputcurrent1'):
      # AC output current of 1st phase 
      value = float(data.get('1ai'))
    elif(sensor_type == 'acoutputcurrent2'):
      # AC output current of 2nd phase 
      value = float(data.get('1aj'))
    elif(sensor_type == 'acoutputcurrent3'):
      # AC output current of 3rd phase 
      value = float(data.get('1ak'))
    elif(sensor_type == 'actualpower'):
      # Total output power of intverter
      if (self.interface_portal.is_online()): 
        value = float(data.get('1ao'))
      else:
        value = 0
    elif(sensor_type == 'energylastmonth'):
      # Total energy produced last month 
      value = float(data.get('1ru'))
    elif(sensor_type == 'energytoday'):
      # Total energy produced today up till now 
      value = float(data.get('1bd'))
    elif(sensor_type == 'energythismonth'):
      # Total energy produced this month up till now 
      value = float(data.get('1be'))
    elif(sensor_type == 'energythisyear'):
      # Total energy produced this year up till now 
      value = float(data.get('1bf'))
    elif(sensor_type == 'energytotal'):
      # Total energy produced up till now 
      value = float(data.get('1bc'))
    
    return value
  
  def update_sensor_values(self):
    """ Update the sensor data values. """
    sensor_types_to_query = list(self._sensors)

    if (self.interface_portal.is_online()):
      portaldata = self.interface_portal.get_portal_data()
      if (portaldata is not None):
        data = portaldata['result']['deviceWapper']['dataJSON']
        for sensor_type in sensor_types_to_query:
          self.sensor_data[sensor_type] = self.decode_data(data, sensor_type)
      else:
        # No valid data received, set all to 0
        for sensor_type in sensor_types_to_query:
          if(sensor_type == 'status'):
            value = 'Offline'
          else:
            self.sensor_data[sensor_type] = None
    

  @Throttle(MIN_TIME_BETWEEN_UPDATES)
  def update(self):
    """ Update the data of the sensors. """
    self.get_statistics()
    
    """ Retrieve the data values for the sensors. """
    self.update_sensor_values()

class SolisPortal():
  """ Class with function for reading data from the Solis portal. """
  
  def __init__(self, domain, username, password, plantid, serial_number):
    """ Initialize the Solis inverter object. """
    self._domain = domain
    self._username = username
    self._password = password
    self._plantid = plantid
    self._serial_number = serial_number
    self._jsondata = None
    self._countdown = 0
    self._session = None
    self._logintime = None
    self._deviceid = None
    # Default english
    self._language = 2
  
  def is_online(self):
    """ 
      Returns true if the portal is online and we're logged in
    """
    online = False
    if ((self._session is not None) and (self._deviceid is not None)):
      online = True
    
    return online

  def get_portal_data(self):
    """
      return the last received json data
    """
    return self._jsondata

  def login(self):
    """ 
      Login to the portal
      Returns a session if successful
    """
    # Create session for requests
    self._session = requests.session()

    #building url
    url = 'http://'+self._domain+'/cpro/login/validateLogin.json'
    params = {
      "userName": self._username,
      "password": self._password,
      "lan": self._language,
      "domain": self._domain,
      "userType": "C"
    }

    #login call
    resultData = self._session.post(url, params=params)
    if (resultData.status_code == requests.codes.ok):
      resultJson = resultData.json()

      if resultJson['result'].get('isAccept') == 1:
        self._logintime = datetime.now()
        _LOGGER.info('Login Successful!')
      else:
        _LOGGER.error('Could not login to %s, are username and password correct?', url)
        self._session = None
    else:
      _LOGGER.error('Uh-oh, trying to login failed with http error ', resultData.status_code)
      self._session = None

  def get_device_id(self):
    """
      After login the inverter list needs to be retrieved in order to get deviceID
      It contains all inverters for plant plant_id with their S/N and deviceID
    """

    self._deviceid = None

    # Get inverter list
    url = 'http://'+self._domain+'/cpro/epc/plantDevice/inverterListAjax.json'
    params = {
      'orderBy': 'updateDate',
      'orderType': 2,
      'pageIndex': 1,
      'plantId': int(self._plantid),
      'sequenceNum': 9,
      'showAddFlg': 1
    }

    cookies = {}
    resultData = self._session.get(url, params=params, cookies=cookies)
    if (resultData.status_code == requests.codes.ok):
      resultJson = resultData.json()

      for record in resultJson['result']['paginationAjax']['data']:
        if (record.get('sn') == self._serial_number):
          self._deviceid = record.get('deviceId')

      if (self._deviceid is None):
        _LOGGER.error('Unable to find inverter with serial %s in plant %s', self._serial_number, self._plantid)
    else:
      _LOGGER.error('Uh-oh, trying to fetch deviceID with http error ', resultData.status_code)


  def get_inverter_details(self):
    """
     Fetch inverter details 
    """
    
    # Get inverter details
    url = 'http://'+self._domain+'/cpro/device/inverter/goDetailAjax.json'
    params = {
      'deviceId': self._deviceid
    }

    cookies = {}
    resultData = self._session.get(url, params=params, cookies=cookies)
    self._jsondata = None
    if (resultData.status_code == requests.codes.ok):
      self._jsondata = resultData.json()
    else:
       _LOGGER.error('Unable to fetch details for device with ID', self._deviceid)

  def get_statistics(self):
    """ Get statistics from the portal. """
    
    """ Login using username and password, but only every HRS_BETWEEN_LOGIN hours """
    if (self._session == None):
      self.login()

    """ Retrieve device id for inverter S/N """
    if (self._session is not None):
      self.get_device_id()

    """ And finally get the inverter details """
    if (self._deviceid is not None):
      self.get_inverter_details()
    else:
      # Reset session and try to login again next time
      self._session = None
      self._logintime = None

    if ((self._logintime + HRS_BETWEEN_LOGIN) < (datetime.now())):
       # Time to login again
       self._session = None
       self._logintime = None


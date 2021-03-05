"""
  Access to the platform 2.0 API for PV monitoring
  Works for m.ginlong.com. Should also work for the myevolvecloud.com portal (not tested)

  For more information: https://github.com/hultenvp/solis-sensor/
"""

import binascii
import hashlib
import logging
import struct
import sys

import asyncio
from datetime import datetime, timedelta
import logging

import aiohttp
import async_timeout

from homeassistant.const import HTTP_OK
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.util import dt as dt_util

# REFRESH CONSTANTS
"""Schedule next call after (minutes)."""
SCHEDULE_OK = 2
"""When an error occurred, new call after (minutes)."""
SCHEDULE_NOK = 1

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '0.0.3'

# Don't login every time
HRS_BETWEEN_LOGIN = timedelta(hours=2)

# Response constants
SUCCESS = 'Success'
CONTENT = 'Content'
STATUS_CODE = 'StatusCode'
MESSAGE = 'Message'

# Status constants
ONLINE = 'Online'
OFFLINE = 'Offline'

"""
  [unit of measurement, key, type, decimal precision]
"""
PORTAL_INVERTER_CONST = {
    'INV_DEVICE_ID':         [None, 'zf', str, None],
    'INV_DATALOGGER_SERIAL': [None, 'za', str, None],
    'INV_TEMPERATURE':       ['°C', '1df',float, 1],
    'LINE_1_VDC':            ['V', '1a', float, 2],
    'LINE_2_VDC':            ['V', '1b', float, 2],
    'LINE_3_VDC':            ['V', '1c', float, 2],
    'LINE_4_VDC':            ['V', '1d', float, 2],
    'LINE_1_ADC':            ['A', '1j', float, 2],
    'LINE_2_ADC':            ['A', '1k', float, 2],
    'LINE_3_ADC':            ['A', '1l', float, 2],
    'LINE_4_ADC':            ['A', '1m', float, 2],
    'PHASE_1_VAC':           ['V', '1af', float, 2],
    'PHASE_2_VAC':           ['V', '1ag', float, 2],
    'PHASE_3_VAC':           ['V', '1ah', float, 2],
    'PHASE_1_AAC':           ['A', '1ai', float, 2],
    'PHASE_2_AAC':           ['A', '1aj', float, 2],
    'PHASE_3_AAC':           ['A', '1ak', float, 2],
    'INV_POWER_AC':          ['W', '1ao', float, 2],
    'INV_ENERGY_LAST_MONTH': ['kWh', '1ru', float, 2],
    'INV_ENERGY_TODAY':      ['kWh', '1bd', float, 2],
    'INV_ENERGY_THIS_MONTH': ['kWh', '1be', float, 2],
    'INV_ENERGY_THIS_YEAR':  ['kWh', '1bf', float, 2],
    'INV_ENERGY_TOTAL_LIFE': ['kWh', '1bc', float, 2]
}

class PortalConfig:
  """ Portal configuration data """

  def __init__(self,  portal_domain, portal_username, portal_password, portal_plantid, inverter_sn):
    self._domain = portal_domain
    self._username = portal_username
    self._password = portal_password
    self._plantid = portal_plantid
    self._inverter_serial = inverter_sn

  @property
  def domain(self):
    return self._domain

  @property
  def username(self):
    return self._username

  @property
  def password(self):
    return self._password

  @property
  def plantid(self):
    return self._plantid

  @property
  def inverter_serial(self):
    return self._inverter_serial


class InverterData(object):
  """ Representation of a Platform 2.0 data object used for retrieving data values. """

  def __init__(self, portal_config, hass, devices):
    """ Initialize Solis data component. """
    self._last_updated = None
    self._energy_yesterday = 0
    self._status = OFFLINE
    self._devices = devices
    self.hass = hass
    self.interface_portal = PortalAPI(hass, portal_config)
    self._sensor_data = {type: None for type in PORTAL_INVERTER_CONST}

  async def update_devices(self):
    """ Update all registered sensors. """
    if not self._devices:
      return
    # Update all devices
    for dev in self._devices:
      dev.data_updated(self)

  def get_inverter_attributes(self):
    """ Return an array with the sensors and their values. """
    return self._sensor_data

  def get_inverter_attribute(self, attribute_key):
    """ Return an attribute's latest value """
    return self._sensor_data[attribute_key][0]

  def get_inverter_attribute_uom(self, attribute_key):
    """ Return an attribute's unit of measurement"""
    return PORTAL_INVERTER_CONST[attribute_key][0]

  def _get_float(self, data, key, precision = 2):
    """ Retrieve 'key' from 'data' as type float with precision 'precision' """
    result = None

    data_raw = data.get(key)
    if (data_raw is not None):
      data_float = float(data_raw)
      # Round to specified precision
      result = round(data_float, precision)
    return result

  def _get_string(self, data, key):
    """ Retrieve 'key' from 'data as type string """
    return data.get(key)

  def _update_attributes(self):
    """ Update the PV attributes with received portal data. """

    status = OFFLINE
    if (self.interface_portal.is_online()):
      portaldata = self.interface_portal.get_portal_data()
      if (portaldata is not None):
        data = portaldata['result']['deviceWapper']['dataJSON']
        # We're online and we have data, so update last_updated
        # Energy_today is not reset at midnight, but in the mornging at sunrise when the inverter switches back on
        if (self._last_updated.day != datetime.now().day)
          # Take snapshot
          self._energy_yesterday = self._sensor_data[INV_ENERGY_TODAY]
        self._last_updated = datetime.now()
        status = ONLINE
        # Fetch all attributes from payload
        for attribute in PORTAL_INVERTER_CONST:
          key = PORTAL_INVERTER_CONST[attribute][1]
          type = PORTAL_INVERTER_CONST[attribute][2]
          precision = PORTAL_INVERTER_CONST[attribute][3]
          if(key == None):
            # Do nothing, no key
            pass
          else:
            if(type == str):
              self._sensor_data[attribute] = self._get_string(data, key)
            elif(type == float):
              self._sensor_data[attribute] = self._get_float(data, key, precision)
    self._status  = status

  async def async_update(self, *_):
    """Update the data from PV Portal."""
    result = await self.interface_portal.async_update()
    if (result == SCHEDULE_OK):
      self._update_attributes()
      await self.update_devices()

    await self.schedule_update(result)

  async def schedule_update(self, minute=1):
    """ Schedule an update after minute minutes. """
    _LOGGER.debug("Scheduling next update in %s minutes.", minute)
    nxt = dt_util.utcnow() + timedelta(minutes=minute)
    async_track_point_in_utc_time(self.hass, self.async_update, nxt)


  @property
  def status(self):
    return self._status

  @property
  def last_updated(self):
    return self._last_updated

  @property
  def serial(self):
    return self.interface_portal.config.inverter_serial

  @property
  def temperature(self):
    return self._sensor_data['INV_TEMPERATURE']

  @property
  def dcinputvoltagepv1(self):
    return self._sensor_data['LINE_1_VDC']

  @property
  def dcinputvoltagepv2(self):
    return self._sensor_data['LINE_2_VDC']

  @property
  def dcinputvoltagepv3(self):
    return self._sensor_data['LINE_3_VDC']

  @property
  def dcinputvoltagepv4(self):
    return self._sensor_data['LINE_4_VDC']

  @property
  def dcinputcurrentpv1(self):
    return self._sensor_data['LINE_1_ADC']

  @property
  def dcinputcurrentpv2(self):
    return self._sensor_data['LINE_2_ADC']

  @property
  def dcinputcurrentpv3(self):
    return self._sensor_data['LINE_3_ADC']

  @property
  def dcinputcurrentpv4(self):
    return self._sensor_data['LINE_4_ADC']

  @property
  def acoutputvoltage1(self):
    return self._sensor_data['PHASE_1_VAC']

  @property
  def acoutputvoltage2(self):
    return self._sensor_data['PHASE_2_VAC']

  @property
  def acoutputvoltage3(self):
    return self._sensor_data['PHASE_3_VAC']

  @property
  def acoutputcurrent1(self):
    return self._sensor_data['PHASE_1_AAC']

  @property
  def acoutputcurrent2(self):
    return self._sensor_data['PHASE_2_AAC']

  @property
  def acoutputcurrent3(self):
    return self._sensor_data['PHASE_3_AAC']

  @property
  def actualpower(self):
    return self._sensor_data['INV_POWER_AC']

  @property
  def energylastmonth(self):
    return self._sensor_data['INV_ENERGY_LAST_MONTH']

  @property
  def energytoday(self):
    energy = self._sensor_data['INV_ENERGY_TODAY']
    # if energy today is still the same as energy yesterday then the 
    # portal has not yet reset energy_today.
    if (energy == self._energy_yesterday)
      energy = 0
    else
      # reset energy_yesterday and use today's value.
      self._energy_yesterday = 0
    return energy;

  @property
  def energythismonth(self):
    return self._sensor_data['INV_ENERGY_THIS_MONTH']

  @property
  def energythisyear(self):
    return self._sensor_data['INV_ENERGY_THIS_YEAR']

  @property
  def energytotal(self):
    return self._sensor_data['INV_ENERGY_TOTAL_LIFE']

  @property
  def devide_id(self):
    return self._sensor_data['INV_DEVICE_ID']

  @property
  def datalogger_serial(self):
    return self._sensor_data['INV_DATALOGGER_SERIAL']


class PortalAPI():
  """ Class with functions for reading data from the Platform 2.0 portal. """

  def __init__(self, hass, config):
    """ Initialize the Solis inverter object. """

    self._hass = hass
    self.config = config
    self._jsondata = None
    self._logintime = None
    self._deviceid = None
    # Default english
    self._language = 2

  def is_online(self):
    """ Returns true if the portal is online and we're logged in """
    online = False
    if ((self._logintime is not None) and (self._deviceid is not None)):
      online = True

    return online

  def get_portal_data(self):
    """ Return the last received json data """
    return self._jsondata

  def get_device_id(self):
    """ Return the device ID of the inverter """
    return self._deviceid

  async def login(self):
    """ Login to the portal. """
    # Building url & params
    url = 'https://'+self.config.domain+'/cpro/login/validateLogin.json'
    params = {
      "userName": self.config.username,
      "password": self.config.password,
      "lan": self._language,
      "domain": self.config.domain,
      "userType": "C"
    }

    # Login call
    result = await self._post_data(url, params)
    if (result[SUCCESS] == True):
      resultJson = result[CONTENT]

      if resultJson['result'].get('isAccept') == 1:
        self._logintime = datetime.now()
        _LOGGER.info('Login Successful!')
      else:
        _LOGGER.error('Could not login to %s, are username and password correct?', url)
        self._logintime = None
    else:
      _LOGGER.error('%s', result[MESSAGE])
      self._logintime = None

  async def update_device_id(self):
    """
      After login the inverter list needs to be retrieved in order to get deviceID
      It contains all inverters for plant plant_id with their S/N and deviceID
    """

    self._deviceid = None

    # Get inverter list
    url = 'http://'+self.config.domain+'/cpro/epc/plantDevice/inverterListAjax.json'
    params = {
      'orderBy': 'updateDate',
      'orderType': 2,
      'pageIndex': 1,
      'plantId': int(self.config.plantid),
      'sequenceNum': 9,
      'showAddFlg': 1
    }

    result = await self._get_data(url, params)

    if (result[SUCCESS] == True):
      resultJson = result[CONTENT]
      for record in resultJson['result']['paginationAjax']['data']:
        if (record.get('sn') == self.config.inverter_serial):
          self._deviceid = record.get('deviceId')

      if (self._deviceid is None):
        _LOGGER.error('Unable to find inverter with serial %s in plant %s', self.config.serial_number, self.config.plantid)
    else:
      # We get here quite often  with  confusing msg.
      _LOGGER.error('%s', result[MESSAGE])
      self._logintime = None


  async def update_inverter_details(self):
    """
    Update inverter details
    """

    # Get inverter details
    url = 'http://'+self.config.domain+'/cpro/device/inverter/goDetailAjax.json'
    params = {
      'deviceId': self._deviceid
    }

    result = await self._get_data(url, params)

    self._jsondata = None
    if (result[SUCCESS] == True):
      self._jsondata = result[CONTENT]
    else:
      _LOGGER.error('Unable to fetch details for device with ID: %s', self._deviceid)
      _LOGGER.error('Message: %s', result[MESSAGE])


  async def _get_data(self, url, params):
    """ Http-get data from specified url. """

    result = {SUCCESS: False, MESSAGE: None, STATUS_CODE: None}
    resp = None
    try:
      websession = async_get_clientsession(self._hass)
      with async_timeout.timeout(10):
        resp = await websession.get(url, params=params)

        result[STATUS_CODE] = resp.status
        result[CONTENT] = await resp.json()
        if resp.status == HTTP_OK:
          result[SUCCESS] = True
        else:
          result[MESSAGE] = "Got http statuscode: %d" % (resp.status)

        return result
    except (asyncio.TimeoutError, aiohttp.ClientError) as err:
      result[MESSAGE] = "%s" % err
      return result
    finally:
      if resp is not None:
        await resp.release()

  async def _post_data(self, url, params):
    """ Http-post data to specified url. """

    result = {SUCCESS: False, MESSAGE: None}
    resp = None
    try:
      websession = async_get_clientsession(self._hass)
      with async_timeout.timeout(10):
        resp = await websession.post(url, params=params)

        result[STATUS_CODE] = resp.status
        result[CONTENT] = await resp.json()
        if resp.status == HTTP_OK:
          result[SUCCESS] = True
        else:
          result[MESSAGE] = "Got http statuscode: %d" % (resp.status)

        return result
    except (asyncio.TimeoutError, aiohttp.ClientError) as err:
      result[MESSAGE] = "%s" % err
      return result
    finally:
      if resp is not None:
        await resp.release()

  async def async_update(self):
    """Update the data from PV portal."""

    result = SCHEDULE_NOK
    # Login using username and password, but only every HRS_BETWEEN_LOGIN hours
    if (self._logintime == None):
      await self.login()

    # Retrieve device id for inverter S/N
    if (self._logintime is not None):
      await self.update_device_id()
      # And finally get the inverter details
      if (self._deviceid is not None):
        await self.update_inverter_details()
        result = SCHEDULE_OK
      else:
        self._logintime = None
    else:
      # Reset session and try to login again next time
      self._logintime = None

    if (self._logintime is not None):
      if ((self._logintime + HRS_BETWEEN_LOGIN) < (datetime.now())):
        # Time to login again
        self._logintime = None

    return result


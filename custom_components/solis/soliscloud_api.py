"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""
from __future__ import annotations

import hashlib
#from hashlib import sha1
import hmac
import base64
import asyncio
from datetime import datetime
from datetime import timezone
from http import HTTPStatus
import json
import logging
import math
from typing import Any
from aiohttp import ClientError, ClientSession
import async_timeout
import yaml

from .ginlong_base import BaseAPI, GinlongData, PortalConfig
from .ginlong_const import *
from .soliscloud_const import *

_LOGGER = logging.getLogger(__name__)

# VERSION
VERSION = '0.4.3'

# API NAME
API_NAME = 'SolisCloud'

# Response constants
SUCCESS = 'Success'
CONTENT = 'Content'
STATUS_CODE = 'StatusCode'
MESSAGE = 'Message'

#VALUE_RECORD = '_from_record'
#VALUE_ELEMENT = ''

VERB = "POST"

INVERTER_DETAIL = '/v1/api/inverterDetail'
PLANT_DETAIL = '/v1/api/stationDetail'
PLANT_LIST = '/v1/api/userStationList'

InverterDataType = dict[str, dict[str, list]]

"""{endpoint: [payload type, {key type, decimal precision}]}"""
INVERTER_DATA: InverterDataType = {
    INVERTER_DETAIL: {
        INVERTER_SERIAL:                  ['sn', str, None],
        INVERTER_PLANT_ID:                ['stationId', str, None],
        INVERTER_DEVICE_ID:               ['id', str, None],
        INVERTER_DATALOGGER_SERIAL:       ['collectorId', str, None],
        # Timestamp of measurement
        INVERTER_TIMESTAMP_UPDATE:        ['dataTimestamp', int, None],
        INVERTER_STATE:                   ['state', int, None],
        INVERTER_TEMPERATURE:             ['inverterTemperature', float, 1],
        INVERTER_POWER_STATE:             ['currentState', int, None],
        INVERTER_ACPOWER:                 ['pac', float, 3],
        INVERTER_ACPOWER_STR:             ['pacStr', str, None],
        INVERTER_ACFREQUENCY:             ['fac', float, 2],
        INVERTER_ENERGY_TODAY:            ['eToday', float, 2], # Default
        INVERTER_ENERGY_THIS_MONTH:       ['eMonth', float, 2],
        INVERTER_ENERGY_THIS_MONTH_STR:   ['eMonthStr', str, None],
        INVERTER_ENERGY_THIS_YEAR:        ['eYear', float, 2],
        INVERTER_ENERGY_THIS_YEAR_STR:    ['eYearStr', str, None],
        INVERTER_ENERGY_TOTAL_LIFE:       ['eTotal', float, 2],
        INVERTER_ENERGY_TOTAL_LIFE_STR:   ['eTotalStr', str, None],
        STRING_COUNT:                     ['dcInputtype', int, None],
        STRING1_VOLTAGE:                  ['uPv1', float, 2],
        STRING2_VOLTAGE:                  ['uPv2', float, 2],
        STRING3_VOLTAGE:                  ['uPv3', float, 2],
        STRING4_VOLTAGE:                  ['uPv4', float, 2],
        STRING1_CURRENT:                  ['iPv1', float, 2],
        STRING2_CURRENT:                  ['iPv2', float, 2],
        STRING3_CURRENT:                  ['iPv3', float, 2],
        STRING4_CURRENT:                  ['iPv4', float, 2],
        STRING1_POWER:                    ['pow1', float, 2], # Undocumented
        STRING2_POWER:                    ['pow2', float, 2], # Undocumented
        STRING3_POWER:                    ['pow3', float, 2], # Undocumented
        STRING4_POWER:                    ['pow4', float, 2], # Undocumented
        PHASE1_VOLTAGE:                   ['uAc1', float, 2],
        PHASE2_VOLTAGE:                   ['uAc2', float, 2],
        PHASE3_VOLTAGE:                   ['uAc3', float, 2],
        PHASE1_CURRENT:                   ['iAc1', float, 2],
        PHASE2_CURRENT:                   ['iAc2', float, 2],
        PHASE3_CURRENT:                   ['iAc3', float, 2],
        BAT_POWER:                        ['batteryPower', float, 3],
        BAT_POWER_STR:                    ['batteryPowerStr', str, None],
        BAT_REMAINING_CAPACITY:           ['batteryCapacitySoc', float, 2],
        BAT_STATE_OF_HEALTH:              ['batteryHealthSoh', float, 2],
        BAT_CURRENT:                      ['storageBatteryCurrent', float, 2],
        BAT_CURRENT_STR:                  ['storageBatteryCurrentStr', str, None],
        BAT_VOLTAGE:                      ['storageBatteryVoltage', float, 2],
        BAT_VOLTAGE_STR:                  ['storageBatteryVoltageStr', str, None],
        BAT_TOTAL_ENERGY_CHARGED:         ['batteryTotalChargeEnergy', float, 3],
        BAT_TOTAL_ENERGY_CHARGED_STR:     ['batteryTotalChargeEnergyStr', str, None],
        BAT_TOTAL_ENERGY_DISCHARGED:      ['batteryTotalDischargeEnergy', float, 3],
        BAT_TOTAL_ENERGY_DISCHARGED_STR:  ['batteryTotalDischargeEnergyStr', str, None],
        BAT_DAILY_ENERGY_CHARGED:         ['batteryTodayChargeEnergy', float, 2],
        BAT_DAILY_ENERGY_DISCHARGED:      ['batteryTodayDischargeEnergy', float, 2],
        GRID_DAILY_ON_GRID_ENERGY:        ['gridSellTodayEnergy', float, 2],
        GRID_DAILY_ON_GRID_ENERGY_STR:    ['gridSellTodayEnergyStr', str, None],
        GRID_DAILY_ENERGY_PURCHASED:      ['gridPurchasedTodayEnergy', float, 2],
        GRID_DAILY_ENERGY_USED:           ['homeLoadTodayEnergy', float, 2],
        GRID_MONTHLY_ENERGY_PURCHASED:    ['gridPurchasedMonthEnergy', float, 2],
        GRID_YEARLY_ENERGY_PURCHASED:     ['gridPurchasedYearEnergy', float, 2],
        GRID_TOTAL_ENERGY_PURCHASED:      ['gridPurchasedTotalEnergy', float, 2],
        GRID_TOTAL_ENERGY_PURCHASED_STR:  ['gridPurchasedTotalEnergyStr', str, None],
        GRID_TOTAL_ON_GRID_ENERGY:        ['gridSellTotalEnergy', float, 2],
        GRID_TOTAL_ON_GRID_ENERGY_STR:    ['gridSellTotalEnergyStr', str, None],
        GRID_TOTAL_POWER:                 ['psum', float, 3],
        GRID_TOTAL_POWER_STR:             ['psumStr', str, None],
        GRID_TOTAL_CONSUMPTION_POWER:     ['familyLoadPower', float, 3],
        GRID_TOTAL_CONSUMPTION_POWER_STR: ['familyLoadPowerStr', str, None],
        GRID_TOTAL_ENERGY_USED:           ['homeLoadTotalEnergy', float, 3],
        GRID_TOTAL_ENERGY_USED_STR:       ['homeLoadTotalEnergyStr', str, None],
        SOC_CHARGING_SET:                 ['socChargingSet', float, 0],
        SOC_DISCHARGE_SET:                ['socDischargeSet', float, 0]
    },
    PLANT_DETAIL: {
        INVERTER_PLANT_NAME:              ['sno', str, None], #stationName no longer available?
        INVERTER_LAT:                     ['latitude', float, 7],
        INVERTER_LON:                     ['longitude', float, 7],
        INVERTER_ADDRESS:                 ['cityStr', str, None],
        INVERTER_ENERGY_TODAY:            ['dayEnergy', float, 2] #If override set
    },
    PLANT_LIST: {
        INVERTER_PLANT_NAME:              ['sno', str, None], #stationName no longer available?
        INVERTER_ADDRESS:                 ['cityStr', str, None],
        INVERTER_ENERGY_TODAY:            ['dayEnergy', float, 2] #If override set
    },
}

class SoliscloudConfig(PortalConfig):
    """ Portal configuration data """

    def __init__(self,
        portal_domain: str,
        portal_username: str,
        portal_key_id: str,
        portal_secret: bytes,
        portal_plantid: str
    ) -> None:
        super().__init__(portal_domain, portal_username, portal_plantid)
        self._key_id: str = portal_key_id
        self._secret: bytes = portal_secret
        self._workarounds = {}
        try:
            with open('/config/custom_components/solis/workarounds.yaml', 'r') as file:
                self._workarounds = yaml.safe_load(file)
                _LOGGER.debug("workarounds: %s", self._workarounds)
        except FileNotFoundError:
            pass

    @property
    def key_id(self) -> str:
        """ Key ID."""
        return self._key_id

    @property
    def secret(self) -> bytes:
        """ API Key."""
        return self._secret

    @property
    def workarounds(self) -> dict[str, Any]:
        """ Return all workaround settings """
        return self._workarounds

class SoliscloudAPI(BaseAPI):
    """Class with functions for reading data from the Soliscloud Portal."""

    def __init__(self, config: SoliscloudConfig) -> None:
        self._config: SoliscloudConfig = config
        self._session: ClientSession | None = None
        self._is_online: bool = False
        self._data: dict[str, str | int | float] = {}
        self._inverter_list: dict[str, str] | None = None

    @property
    def api_name(self) -> str:
        """ Return name of the API."""
        return API_NAME

    @property
    def config(self) -> SoliscloudConfig:
        """ Config this for this API instance."""
        return self._config

    @property
    def is_online(self) -> bool:
        """ Returns if we are logged in."""
        return self._is_online

    async def login(self, session: ClientSession) -> bool:
        """See if we can build a list of inverters"""
        self._session = session
        self._inverter_list = None

        # Request inverter list
        self._inverter_list = await self.fetch_inverter_list(self.config.plant_id)
        if len(self._inverter_list)==0:
            _LOGGER.warning("No inverters found")
            self._is_online = False
        else:
            _LOGGER.info("Login successful")
            _LOGGER.debug("Found inverters: %s", list(self._inverter_list.keys()))
            self._is_online = True
            try:
                data = await self.fetch_inverter_data(next(iter(self._inverter_list)))
                self._plant_name = getattr(data, INVERTER_PLANT_NAME)
            except AttributeError:
                _LOGGER.info("Failed to acquire plant name, login failed")
                self._is_online = False
        return self.is_online

    async def logout(self) -> None:
        """Hand back session """
        self._session = None
        self._is_online = False
        self._inverter_list = None

    async def fetch_inverter_list(self, plant_id: str) -> dict[str, str]:
        """
        Fetch return list of inverters { inverter serial : device_id }
        """

        device_ids = {}

        params = {
            'stationId': plant_id
        }
        result = await self._post_data_json('/v1/api/inverterList', params)

        if result[SUCCESS] is True:
            result_json: dict = result[CONTENT]
            if result_json['code'] != '0':
                _LOGGER.info("%s responded with error: %s:%s",INVERTER_DETAIL, \
                    result_json['code'], result_json['msg'])
                return device_ids
            try:
                for record in result_json['data']['page']['records']:
                    serial = record.get('sn')
                    device_id = record.get('id')
                    device_ids[serial] = device_id
            except TypeError:
                _LOGGER.debug("Response contains unexpected data: %s", result_json)
        elif result[STATUS_CODE] == 408:
            now = datetime.now().strftime("%d-%m-%Y %H:%M GMT")
            _LOGGER.warning("Your system time must be set correctly for this integration \
            to work, your time is %s", now)
        return device_ids

    async def fetch_inverter_data(self, inverter_serial: str) -> GinlongData | None:
        """
        Fetch data for given inverter.
        Collect available data from payload and store as GinlongData object
        """

        _LOGGER.debug("Fetching data for serial: %s", inverter_serial)
        self._data = {}
        if self.is_online:
            if self._inverter_list is not None and inverter_serial in self._inverter_list:
                device_id = self._inverter_list[inverter_serial]
                # Throttle http calls to avoid 502 error
                await asyncio.sleep(1)
                payload = await self._get_inverter_details(device_id, inverter_serial)
                await asyncio.sleep(1)
                payload2 = await self._get_station_from_list(self.config.plant_id)
                if payload is not None:
                    #_LOGGER.debug("%s", payload)
                    self._collect_inverter_data(payload)
                    self._post_process()
                if payload2 is not None:
                    self._collect_station_data(payload2)
                if self._data is not None and INVERTER_SERIAL in self._data:
                    return GinlongData(self._data)
                _LOGGER.debug("Unexpected response from server: %s", payload)
        return None


    async def _get_inverter_details(self,
        device_id: str,
        device_serial: str
    ) -> dict[str, Any] | None:
        """
        Update inverter details
        """

        # Get inverter details
        params = {
            'id': device_id,
            'sn': device_serial
        }

        result = await self._post_data_json(INVERTER_DETAIL, params)

        jsondata = None
        if result[SUCCESS] is True:
            jsondata = result[CONTENT]
            if jsondata['code'] != '0':
                _LOGGER.info("%s responded with error: %s:%s",INVERTER_DETAIL, \
                    jsondata['code'], jsondata['msg'])
                return None
        else:
            _LOGGER.info('Unable to fetch details for device with ID: %s', device_id)
        return jsondata

    def _collect_inverter_data(self, payload: dict[str, Any]) -> None:
        """ Fetch dynamic properties """
        jsondata = payload['data']
        attributes = INVERTER_DATA[INVERTER_DETAIL]
        collect_energy_today = True
        try:
            collect_energy_today = \
                not self.config.workarounds['use_energy_today_from_plant']
        except KeyError:
            pass
        if collect_energy_today:
            _LOGGER.debug("Using inverterDetail for energy_today")

        for dictkey in attributes:
            key = attributes[dictkey][0]
            type_ = attributes[dictkey][1]
            precision = attributes[dictkey][2]
            if key is not None:
                value = None
                if key != INVERTER_ENERGY_TODAY or collect_energy_today:
                    value = self._get_value(jsondata, key, type_, precision)
                if value is not None:
                    self._data[dictkey] = value

    async def _get_station_details(self, plant_id: str) -> dict[str, str] | None:
        """
        Fetch Station Details
        """

        params = {
            'id': plant_id
        }
        result = await self._post_data_json(PLANT_DETAIL, params)

        if result[SUCCESS] is True:
            jsondata : dict[str, str] = result[CONTENT]
            if jsondata['code'] == '0':
                return jsondata
            else:
                _LOGGER.info("%s responded with error: %s:%s",PLANT_DETAIL, \
                    jsondata['code'], jsondata['msg'])
        else:
            _LOGGER.info('Unable to fetch details for Station with ID: %s', plant_id)
        return None

    async def _get_station_from_list(self, plant_id: str) -> dict[str, str] | None:
        """
        Fetch Station from Station List
        """

        params = {}
        result = await self._post_data_json(PLANT_LIST, params)

        if result[SUCCESS] is True:
            jsondata : dict[str, str] = result[CONTENT]
            if jsondata['code'] == '0':
                try:
                    for record in jsondata['data']['page']['records']:
                        if int(record.get('id')) == int(plant_id):
                            return record
                    _LOGGER.warning("Not able to find station %s", plant_id)
                except TypeError:
                    _LOGGER.debug("Response contains unexpected data: %s", jsondata)
            else:
                _LOGGER.info("%s responded with error: %s:%s",PLANT_LIST, \
                    jsondata['code'], jsondata['msg'])
        else:
            _LOGGER.info('Unable to fetch details for Station with ID: %s', plant_id)
        return None

    def _collect_station_data(self, payload: dict[str, Any]) -> None:
        """ Fetch dynamic properties """
        jsondata = payload
        attributes = INVERTER_DATA[PLANT_DETAIL]
        collect_energy_today = False
        try:
            collect_energy_today = \
                self.config.workarounds['use_energy_today_from_plant']
        except KeyError:
            pass
        if collect_energy_today:
            _LOGGER.debug("Using stationDetail for energy_today")

        for dictkey in attributes:
            key = attributes[dictkey][0]
            type_ = attributes[dictkey][1]
            precision = attributes[dictkey][2]
            if key is not None:
                value = None
                if key != INVERTER_ENERGY_TODAY or collect_energy_today:
                    value = self._get_value(jsondata, key, type_, precision)
                if value is not None:
                    self._data[dictkey] = value


    def _post_process(self) -> None:
        """ Cleanup received data. """
        if self._data:
            # Fix timestamps
            try:
                self._data[INVERTER_TIMESTAMP_UPDATE] = \
                    float(self._data[INVERTER_TIMESTAMP_UPDATE])/1000
            except KeyError:
                pass

            # Convert kW into W, etc. depending on unit returned from API.
            self._fix_units(GRID_TOTAL_POWER, GRID_TOTAL_POWER_STR)
            self._fix_units(BAT_POWER, BAT_POWER_STR)
            self._fix_units(BAT_CURRENT, BAT_CURRENT_STR)
            self._fix_units(BAT_VOLTAGE, BAT_VOLTAGE_STR)
            self._fix_units(BAT_TOTAL_ENERGY_CHARGED, BAT_TOTAL_ENERGY_CHARGED_STR)
            self._fix_units(BAT_TOTAL_ENERGY_DISCHARGED, BAT_TOTAL_ENERGY_DISCHARGED_STR)
            self._fix_units(GRID_TOTAL_CONSUMPTION_POWER, GRID_TOTAL_CONSUMPTION_POWER_STR)
            self._fix_units(GRID_TOTAL_ENERGY_USED, GRID_TOTAL_ENERGY_USED_STR)
            self._fix_units(INVERTER_ACPOWER, INVERTER_ACPOWER_STR)
            self._fix_units(INVERTER_ENERGY_THIS_MONTH, INVERTER_ENERGY_THIS_MONTH_STR)
            self._fix_units(INVERTER_ENERGY_THIS_YEAR, INVERTER_ENERGY_THIS_YEAR_STR)
            self._fix_units(INVERTER_ENERGY_TOTAL_LIFE, INVERTER_ENERGY_TOTAL_LIFE_STR)
            self._fix_units(GRID_TOTAL_ENERGY_PURCHASED, GRID_TOTAL_ENERGY_PURCHASED_STR)
            self._fix_units(GRID_DAILY_ON_GRID_ENERGY, GRID_DAILY_ON_GRID_ENERGY_STR)
            self._fix_units(GRID_TOTAL_ON_GRID_ENERGY, GRID_TOTAL_ON_GRID_ENERGY_STR)

            # Just temporary till SolisCloud is fixed
            try:
                if self.config.workarounds['correct_daily_on_grid_energy_enabled']:
                    self._data[GRID_DAILY_ON_GRID_ENERGY] = \
                        float(self._data[GRID_DAILY_ON_GRID_ENERGY])*10
            except KeyError:
                pass

            # turn batteryPower negative when discharging (fix for https://github.com/hultenvp/solis-sensor/issues/158)
            try:
                self._data[BAT_POWER] = math.copysign(self._data[BAT_POWER],self._data[BAT_CURRENT])
            except KeyError:
                pass

            # Unused phases are still in JSON payload as 0.0, remove them
            # FIXME: use acOutputType
            self._purge_if_unused(0.0, PHASE1_CURRENT, PHASE1_VOLTAGE)
            self._purge_if_unused(0.0, PHASE2_CURRENT, PHASE2_VOLTAGE)
            self._purge_if_unused(0.0, PHASE3_CURRENT, PHASE3_VOLTAGE)

            # Unused PV chains are still in JSON payload as 0, remove them
            # FIXME: use dcInputtype (NB num + 1) Unfortunately so are chains that are
            # just making 0 voltage. So this is too simplistic.
            # mypy trips over self_data[STRING_COUNT] as it could be of type str, int or float
            # needs to be fixed at some point in time, but this works.
            for i, stringlist in enumerate(STRING_LISTS):
                if i > int(self._data[STRING_COUNT]):
                    self._purge_if_unused(0, *stringlist)

    def _fix_units(self, num_key: str, units_key: str) -> None:
        """ Convert numeric values according to the units reported by the API. """
        try:
            if self._data[units_key] == "kW":
                self._data[num_key] = float(self._data[num_key])*1000
                self._data[units_key] = "W"

            elif self._data[units_key] == "MWh":
                self._data[num_key] = float(self._data[num_key])*1000
                self._data[units_key] = "kWh"

            elif self._data[units_key] == "GWh":
                self._data[num_key] = float(self._data[num_key])*1000*1000
                self._data[units_key] = "kWh"

        except KeyError:
            pass

    def _purge_if_unused(self, value: Any, *elements: str) -> None:
        for element in elements:
            try:
                if self._data[element] != value:
                    return
            except KeyError:
                return
        for element in elements:
            self._data.pop(element)

    def _get_value(self,
        data: dict[str, Any], key: str, type_: type, precision: int = 2
    ) -> str | int | float | None:
        """ Retrieve 'key' from 'data' as type 'type_' with precision 'precision' """
        result : str | int | float | None = None

        data_raw = data.get(key)
        if data_raw is not None:
            try:
                if type_ is int:
                    result = int(float(data_raw))
                else:
                    result = type_(data_raw)
                # Round to specified precision
                if type_ is float:
                    result = round(float(result), precision) # type: ignore
            except ValueError:
                _LOGGER.debug("Failed to convert %s to type %s, raw value = %s", \
                    key, type_, data_raw)
        return result

    async def _get_data(self,
            url: str,
            params: dict[str, Any]
        ) -> dict[str, Any]:
        """ Http-get data from specified url. """

        result: dict[str, Any] = {SUCCESS: False, MESSAGE: None, STATUS_CODE: None}
        resp = None
        if self._session is None:
            return result
        try:
            async with async_timeout.timeout(10):
                resp = await self._session.get(url, params=params)

                result[STATUS_CODE] = resp.status
                result[CONTENT] = await resp.json()
                if resp.status == HTTPStatus.OK:
                    result[SUCCESS] = True
                    result[MESSAGE] = "OK"
                else:
                    result[MESSAGE] = "Got http statuscode: %d" % (resp.status)
                return result
        except (asyncio.TimeoutError, ClientError) as err:
            result[MESSAGE] = "Exception: %s" % err.__class__
            _LOGGER.debug("Error: %s", result[MESSAGE])
            return result
        finally:
            if resp is not None:
                await resp.release()

    def _prepare_header(self, body: dict[str, str], canonicalized_resource: str) -> dict[str, str]:
        content_md5 = base64.b64encode(
            hashlib.md5(json.dumps(body,separators=(",", ":")).encode('utf-8')).digest()
        ).decode('utf-8')

        content_type = "application/json"

        now = datetime.now(timezone.utc)
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        encrypt_str = (VERB + "\n"
            + content_md5 + "\n"
            + content_type + "\n"
            + date + "\n"
            + canonicalized_resource
        )
        hmac_obj = hmac.new(
            self.config.secret,
            msg=encrypt_str.encode('utf-8'),
            digestmod=hashlib.sha1
        )
        sign = base64.b64encode(hmac_obj.digest())
        authorization = "API " + self.config.key_id + ":" + sign.decode('utf-8')
        
        header: dict [str, str] = {
            "Content-MD5":content_md5,
            "Content-Type":content_type,
            "Date":date,
            "Authorization":authorization
        }
        return header


    async def _post_data_json(self,
        canonicalized_resource: str,
        params: dict[str, Any]) -> dict[str, Any]:
        """ Http-post data to specified domain/canonicalized_resource. """

        header: dict[str, str] = self._prepare_header(params, canonicalized_resource)
        result: dict[str, Any] = {SUCCESS: False, MESSAGE: None, STATUS_CODE: None}
        resp = None
        if self._session is None:
            return result
        try:
            async with async_timeout.timeout(10):
                url = f"{self.config.domain}{canonicalized_resource}"
                resp = await self._session.post(url, json=params, headers=header)

                result[STATUS_CODE] = resp.status
                result[CONTENT] = await resp.json()
                if resp.status == HTTPStatus.OK:
                    result[SUCCESS] = True
                    result[MESSAGE] = "OK"
                else:
                    result[MESSAGE] = "Got http statuscode: %d" % (resp.status)
        except (asyncio.TimeoutError, ClientError) as err:
            result[MESSAGE] = f"{repr(err)}"
            _LOGGER.debug("Error from URI (%s) : %s", canonicalized_resource, result[MESSAGE])
        finally:
            if resp is not None:
                await resp.release()
            return result

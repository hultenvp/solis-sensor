"""
  Constants

  For more information: https://github.com/hultenvp/solis-sensor/
"""
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
)

from homeassistant.const import ( 
    TEMP_CELSIUS,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY)

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
    'status':                   ['Status', None, 'mdi:solar-power', None, None],
    'temperature':              ['Temperature', TEMP_CELSIUS, 'mdi:thermometer', DEVICE_CLASS_TEMPERATURE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv1':        ['DC Voltage PV1', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv2':        ['DC Voltage PV2', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv3':        ['DC Voltage PV3', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputvoltagepv4':        ['DC Voltage PV4', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv1':        ['DC Current PV1', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv2':        ['DC Current PV2', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv3':        ['DC Current PV3', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'dcinputcurrentpv4':        ['DC Current PV4', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage1':         ['AC Voltage R', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage2':         ['AC Voltage S', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputvoltage3':         ['AC Voltage T', 'V', 'mdi:flash-outline', DEVICE_CLASS_VOLTAGE, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent1':         ['AC Current R', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent2':         ['AC Current S', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'acoutputcurrent3':         ['AC Current T', 'A', 'mdi:flash-outline', DEVICE_CLASS_CURRENT, STATE_CLASS_MEASUREMENT],
    'actualpower':              ['AC Output Total Power', 'W', 'mdi:weather-sunny', DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT], 
    'energylastmonth':          ['Energy Last Month', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energytoday':              ['Energy Today', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energythismonth':          ['Energy This Month', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energythisyear':           ['Energy This Year', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'energytotal':              ['Energy Total', 'kWh', 'mdi:flash-outline', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'batcapacityremaining':     ['Remaining battery capacity', '%', 'mdi:battery', DEVICE_CLASS_BATTERY, STATE_CLASS_MEASUREMENT],
    'battotalenergycharged':    ['Total Energy Charged', 'kWh', 'mdi:battery-plus', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'battotalenergydischarged': ['Total Energy Discharged', 'kWh', 'mdi:battery-minus', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'batdailyenergycharged':    ['Daily Energy Charged', 'kWh', 'mdi:battery-plus', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'batdailyenergydischarged': ['Daily Energy Discharged', 'kWh', 'mdi:battery-minus', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'griddailyongridenergy':    ['Daily On-grid Energy', 'kWh', 'mdi:transmission-tower-import', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'griddailyenergypurchased': ['Daily Grid Energy Purchased', 'kWh', 'mdi:transmission-tower-export', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'griddailyenergyused':      ['Daily Grid Energy Used', 'kWh', 'mdi:transmission-tower', DEVICE_CLASS_ENERGY, STATE_CLASS_TOTAL_INCREASING],
    'gridpowergridtotalpower':  ['Power Grid total power', 'W', 'mdi:home-export-outline', DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT],
    'gridtotalconsumptionpower':['Total Consumption power', 'W', 'mdi:home-import-outline', DEVICE_CLASS_POWER, STATE_CLASS_MEASUREMENT],
}

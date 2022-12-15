"""Constants
For more information: https://github.com/hultenvp/solis-sensor/
"""
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
)

from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    FREQUENCY_HERTZ,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_MEGA_WATT_HOUR,
    POWER_WATT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_BATTERY)

from .ginlong_const import *

CONF_PORTAL_DOMAIN = 'portal_domain'
CONF_PORTAL_VERSION = 'portal_version'
CONF_USERNAME = 'portal_username'
CONF_PASSWORD = 'portal_password'
CONF_SECRET = 'portal_secret'
CONF_KEY_ID = 'portal_key_id'
CONF_PLANT_ID = 'portal_plant_id'

DOMAIN = "solis"
SENSOR_PREFIX = 'Solis'
DEFAULT_DOMAIN = 'https://m.ginlong.com'

# Supported sensor types:
# Key: ['label', unit, icon, device class, state class, api_attribute_name]
SENSOR_TYPES = {
    'inverterpowerstate': [
        'Power State',
        None,
        'mdi:power',
        None,
        STATE_CLASS_MEASUREMENT,
        INVERTER_POWER_STATE
    ],
    'inverterstate': [
        'State',
        None,
        'mdi:state-machine',
        None,
        STATE_CLASS_MEASUREMENT,
        INVERTER_STATE
    ],
    'timestamponline': [
        'Timestamp Inverter Online',
        None,
        'mdi:calendar-clock',
        None,
        STATE_CLASS_MEASUREMENT,
        INVERTER_TIMESTAMP_ONLINE
    ],
    'timestampmeasurement': [
        'Timestamp Measurements Received',
        None,
        'mdi:calendar-clock',
        None,
        STATE_CLASS_MEASUREMENT,
        INVERTER_TIMESTAMP_UPDATE
    ],
    'status': [
        'Status',
        None,
        'mdi:solar-power',
        None,
        None,
        'status'
    ],
    'temperature': [
        'Temperature',
        TEMP_CELSIUS,
        'mdi:thermometer',
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
        INVERTER_TEMPERATURE
    ],
    'radiatortemperature1': [
        'Radiator temperature 1', # Solarman only
        TEMP_CELSIUS,
        'mdi:thermometer',
        DEVICE_CLASS_TEMPERATURE,
        STATE_CLASS_MEASUREMENT,
        RADIATOR1_TEMP
    ],
    'dcinputvoltagepv1': [
        'DC Voltage PV1',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        STRING1_VOLTAGE
    ],
    'dcinputvoltagepv2': [
        'DC Voltage PV2',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        STRING2_VOLTAGE
    ],
    'dcinputvoltagepv3': [
        'DC Voltage PV3',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        STRING3_VOLTAGE
    ],
    'dcinputvoltagepv4': [
        'DC Voltage PV4',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        STRING4_VOLTAGE
    ],
    'dcinputcurrentpv1': [
        'DC Current PV1',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        STRING1_CURRENT
    ],
    'dcinputcurrentpv2': [
        'DC Current PV2',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        STRING2_CURRENT
    ],
    'dcinputcurrentpv3': [
        'DC Current PV3',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        STRING3_CURRENT
    ],
    'dcinputcurrentpv4': [
        'DC Current PV4',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        STRING4_CURRENT
    ],
    'dcinputpowerpv1': [
        'DC Power PV1',
        POWER_WATT,
        'mdi:solar-power',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        STRING1_POWER
    ],
    'dcinputpowerpv2': [
        'DC Power PV2',
        POWER_WATT,
        'mdi:solar-power',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        STRING2_POWER
    ],
    'dcinputpowerpv3': [
        'DC Power PV3',
        POWER_WATT,
        'mdi:solar-power',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        STRING3_POWER
    ],
    'dcinputpowerpv4': [
        'DC Power PV4',
        POWER_WATT,
        'mdi:solar-power',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        STRING4_POWER
    ],
    'acoutputvoltage1': [
        'AC Voltage R',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        PHASE1_VOLTAGE
    ],
    'acoutputvoltage2': [
        'AC Voltage S',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        PHASE2_VOLTAGE
    ],
    'acoutputvoltage3': [
        'AC Voltage T',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:flash-outline',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        PHASE3_VOLTAGE
    ],
    'acoutputcurrent1': [
        'AC Current R',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        PHASE1_CURRENT
    ],
    'acoutputcurrent2': [
        'AC Current S',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        PHASE2_CURRENT
    ],
    'acoutputcurrent3': [
        'AC Current T',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:flash-outline',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        PHASE3_CURRENT
    ],
    'actualpower': [
        'AC Output Total Power',
        POWER_WATT,
        'mdi:solar-power',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        INVERTER_ACPOWER
    ],
    'acfrequency': [
        'AC Frequency',
        FREQUENCY_HERTZ,
        'mdi:sine-wave',
        None,
        STATE_CLASS_MEASUREMENT,
        INVERTER_ACFREQUENCY
    ],
    'energylastmonth': [
        'Energy Last Month',
        ENERGY_KILO_WATT_HOUR,
        'mdi:flash-outline',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        INVERTER_ENERGY_LAST_MONTH
    ],
    'energytoday': [
        'Energy Today',
        ENERGY_KILO_WATT_HOUR,
        'mdi:flash-outline',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        INVERTER_ENERGY_TODAY
    ],
    'energythismonth': [
        'Energy This Month',
        ENERGY_KILO_WATT_HOUR,
        'mdi:flash-outline',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        INVERTER_ENERGY_THIS_MONTH
    ],
    'energythisyear': [
        'Energy This Year',
        ENERGY_KILO_WATT_HOUR,
        'mdi:flash-outline',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        INVERTER_ENERGY_THIS_YEAR
    ],
    'energytotal': [
        'Energy Total',
        ENERGY_KILO_WATT_HOUR,
        'mdi:flash-outline',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        INVERTER_ENERGY_TOTAL_LIFE
    ],
    'batpack1capacityremaining': [
        'Battery pack 1 remaining battery capacity', # Solarman only
        PERCENTAGE,
        'mdi:battery',
        DEVICE_CLASS_BATTERY,
        STATE_CLASS_MEASUREMENT,
        BAT1_REMAINING_CAPACITY
    ],
    'batpower': [
        'Battery Power',
        POWER_WATT,
        'mdi:battery',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        BAT_POWER
    ],
    'batvoltage': [
        'Battery Voltage',
        ELECTRIC_POTENTIAL_VOLT,
        'mdi:battery',
        DEVICE_CLASS_VOLTAGE,
        STATE_CLASS_MEASUREMENT,
        BAT_VOLTAGE
    ],
    'batstatus': [ # Key: ['label', unit, icon, device class, state class, api_attribute_name]
        'Battery Status',
        None,
        'mdi:battery',
        None,
        None,
        BAT_STATUS
    ],
    'batcurrent': [
        'Battery Current',
        ELECTRIC_CURRENT_AMPERE,
        'mdi:battery',
        DEVICE_CLASS_CURRENT,
        STATE_CLASS_MEASUREMENT,
        BAT_CURRENT
    ],
    'batcapacityremaining': [
        'Remaining Battery Capacity',
        PERCENTAGE,
        'mdi:battery',
        DEVICE_CLASS_BATTERY,
        STATE_CLASS_MEASUREMENT,
        BAT_REMAINING_CAPACITY
    ],
    'battotalenergycharged': [
        'Total Energy Charged',
        ENERGY_KILO_WATT_HOUR,
        'mdi:battery-plus',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        BAT_TOTAL_ENERGY_CHARGED
    ],
    'battotalenergydischarged': [
        'Total Energy Discharged',
        ENERGY_KILO_WATT_HOUR,
        'mdi:battery-minus',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        BAT_TOTAL_ENERGY_DISCHARGED
    ],
    'batdailyenergycharged': [
        'Daily Energy Charged',
        ENERGY_KILO_WATT_HOUR,
        'mdi:battery-plus',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        BAT_DAILY_ENERGY_CHARGED
    ],
    'batdailyenergydischarged': [
        'Daily Energy Discharged',
        ENERGY_KILO_WATT_HOUR,
        'mdi:battery-minus',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        BAT_DAILY_ENERGY_DISCHARGED
    ],
    'griddailyongridenergy': [
        'Daily On-grid Energy',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_DAILY_ON_GRID_ENERGY
    ],
    'griddailyenergypurchased': [
        'Daily Grid Energy Purchased',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_DAILY_ENERGY_PURCHASED
    ],
    'griddailyenergyused': [
        'Daily Grid Energy Used',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_DAILY_ENERGY_USED
    ],
    'gridmonthlyenergypurchased': [
        'Monthly Grid Energy Purchased',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_MONTHLY_ENERGY_PURCHASED
    ],
    'gridmonthlyenergyused': [
        'Monthly Grid Energy Used',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_MONTHLY_ENERGY_USED
    ],
    'gridyearlyenergypurchased': [
        'Yearly Grid Energy Purchased',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_YEARLY_ENERGY_PURCHASED
    ],
    'gridyearlyenergyused': [
        'Yearly Grid Energy Used',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_YEARLY_ENERGY_USED
    ],
    'gridtotalongridenergy': [
        'Total On-grid Energy',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_TOTAL_ON_GRID_ENERGY
    ],
    'gridtotalconsumptionenergy':[
        'Total Consumption Energy',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_TOTAL_CONSUMPTION_ENERGY
    ],
    'gridpowergridtotalpower': [
        'Power Grid total power',
        POWER_WATT,
        'mdi:home-export-outline',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        GRID_TOTAL_POWER
    ],
    'gridtotalconsumptionpower': [
        'Total Consumption power',
        POWER_WATT,
        'mdi:home-import-outline',
        DEVICE_CLASS_POWER,
        STATE_CLASS_MEASUREMENT,
        GRID_TOTAL_CONSUMPTION_POWER
    ],
    'gridtotalenergypurchased': [
        'Total Energy Purchased',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_TOTAL_ENERGY_PURCHASED
    ],
    'gridtotalenergyused': [
        'Total Energy Used',
        ENERGY_KILO_WATT_HOUR,
        'mdi:transmission-tower',
        DEVICE_CLASS_ENERGY,
        STATE_CLASS_TOTAL_INCREASING,
        GRID_TOTAL_ENERGY_USED
    ],
    'batstateofhealth': [
        'Battery State Of Health',
        PERCENTAGE,
        'mdi:battery',
        DEVICE_CLASS_BATTERY,
        STATE_CLASS_MEASUREMENT,
        BAT_STATE_OF_HEALTH
    ],
    'socChargingSet': [
        'Force Charge SOC',
        PERCENTAGE,
        'mdi:battery',
        DEVICE_CLASS_BATTERY,
        STATE_CLASS_MEASUREMENT,
        SOC_CHARGING_SET
    ],
    'socDischargeSet': [
        'Force Discharge SOC',
        PERCENTAGE,
        'mdi:battery',
        DEVICE_CLASS_BATTERY,
        STATE_CLASS_MEASUREMENT,
        SOC_DISCHARGE_SET
    ],
}

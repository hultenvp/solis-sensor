"""Constants
For more information: https://github.com/hultenvp/solis-sensor/
"""
from homeassistant.components.sensor import (
    SensorStateClass,
    SensorDeviceClass,
)

from homeassistant.const import (
    UnitOfPower,
    UnitOfApparentPower,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfFrequency,
    POWER_VOLT_AMPERE_REACTIVE,
    PERCENTAGE)

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
DEFAULT_DOMAIN = 'https://www.soliscloud.com:13333'

# Supported sensor types:
# Key: ['label', unit, icon, device class, state class, api_attribute_name]
SENSOR_TYPES = {
    'inverterpowerstate': [
        'Power State',
        None,
        'mdi:power',
        None,
        SensorStateClass.MEASUREMENT,
        INVERTER_POWER_STATE
    ],
    'inverterstate': [
        'State',
        None,
        'mdi:state-machine',
        None,
        SensorStateClass.MEASUREMENT,
        INVERTER_STATE
    ],
    'timestamponline': [
        'Timestamp Inverter Online',
        None,
        'mdi:calendar-clock',
        None,
        SensorStateClass.MEASUREMENT,
        INVERTER_TIMESTAMP_ONLINE
    ],
    'timestampmeasurement': [
        'Timestamp Measurements Received',
        None,
        'mdi:calendar-clock',
        None,
        SensorStateClass.MEASUREMENT,
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
        UnitOfTemperature.CELSIUS,
        'mdi:thermometer',
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        INVERTER_TEMPERATURE
    ],
    'radiatortemperature1': [
        'Radiator temperature 1', # Solarman only
        UnitOfTemperature.CELSIUS,
        'mdi:thermometer',
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        RADIATOR1_TEMP
    ],
    'dcinputvoltagepv1': [
        'DC Voltage PV1',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        STRING1_VOLTAGE
    ],
    'dcinputvoltagepv2': [
        'DC Voltage PV2',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        STRING2_VOLTAGE
    ],
    'dcinputvoltagepv3': [
        'DC Voltage PV3',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        STRING3_VOLTAGE
    ],
    'dcinputvoltagepv4': [
        'DC Voltage PV4',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        STRING4_VOLTAGE
    ],
    'dcinputcurrentpv1': [
        'DC Current PV1',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        STRING1_CURRENT
    ],
    'dcinputcurrentpv2': [
        'DC Current PV2',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        STRING2_CURRENT
    ],
    'dcinputcurrentpv3': [
        'DC Current PV3',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        STRING3_CURRENT
    ],
    'dcinputcurrentpv4': [
        'DC Current PV4',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        STRING4_CURRENT
    ],
    'dcinputpowerpv1': [
        'DC Power PV1',
        UnitOfPower.WATT,
        'mdi:solar-power',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        STRING1_POWER
    ],
    'dcinputpowerpv2': [
        'DC Power PV2',
        UnitOfPower.WATT,
        'mdi:solar-power',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        STRING2_POWER
    ],
    'dcinputpowerpv3': [
        'DC Power PV3',
        UnitOfPower.WATT,
        'mdi:solar-power',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        STRING3_POWER
    ],
    'dcinputpowerpv4': [
        'DC Power PV4',
        UnitOfPower.WATT,
        'mdi:solar-power',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        STRING4_POWER
    ],
    'acoutputvoltage1': [
        'AC Voltage R',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        PHASE1_VOLTAGE
    ],
    'acoutputvoltage2': [
        'AC Voltage S',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        PHASE2_VOLTAGE
    ],
    'acoutputvoltage3': [
        'AC Voltage T',
        UnitOfElectricPotential.VOLT,
        'mdi:flash-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        PHASE3_VOLTAGE
    ],
    'acoutputcurrent1': [
        'AC Current R',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        PHASE1_CURRENT
    ],
    'acoutputcurrent2': [
        'AC Current S',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        PHASE2_CURRENT
    ],
    'acoutputcurrent3': [
        'AC Current T',
        UnitOfElectricCurrent.AMPERE,
        'mdi:flash-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        PHASE3_CURRENT
    ],
    'actualpower': [
        'AC Output Total Power',
        UnitOfPower.WATT,
        'mdi:solar-power',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        INVERTER_ACPOWER
    ],
    'acfrequency': [
        'AC Frequency',
        UnitOfFrequency.HERTZ,
        'mdi:sine-wave',
        None,
        SensorStateClass.MEASUREMENT,
        INVERTER_ACFREQUENCY
    ],
    'energylastmonth': [
        'Energy Last Month',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:flash-outline',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        INVERTER_ENERGY_LAST_MONTH
    ],
    'energytoday': [
        'Energy Today',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:flash-outline',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        INVERTER_ENERGY_TODAY
    ],
    'energythismonth': [
        'Energy This Month',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:flash-outline',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        INVERTER_ENERGY_THIS_MONTH
    ],
    'energythisyear': [
        'Energy This Year',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:flash-outline',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        INVERTER_ENERGY_THIS_YEAR
    ],
    'energytotal': [
        'Energy Total',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:flash-outline',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        INVERTER_ENERGY_TOTAL_LIFE
    ],
    'batpack1capacityremaining': [
        'Battery pack 1 remaining battery capacity', # Solarman only
        PERCENTAGE,
        'mdi:battery',
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        BAT1_REMAINING_CAPACITY
    ],
    'batpower': [
        'Battery Power',
        UnitOfPower.WATT,
        'mdi:battery',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        BAT_POWER
    ],
    'batvoltage': [
        'Battery Voltage',
        UnitOfElectricPotential.VOLT,
        'mdi:battery',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
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
        UnitOfElectricCurrent.AMPERE,
        'mdi:battery',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        BAT_CURRENT
    ],
    'batcapacityremaining': [
        'Remaining Battery Capacity',
        PERCENTAGE,
        'mdi:battery',
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        BAT_REMAINING_CAPACITY
    ],
    'battotalenergycharged': [
        'Total Energy Charged',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:battery-plus',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        BAT_TOTAL_ENERGY_CHARGED
    ],
    'battotalenergydischarged': [
        'Total Energy Discharged',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:battery-minus',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        BAT_TOTAL_ENERGY_DISCHARGED
    ],
    'batdailyenergycharged': [
        'Daily Energy Charged',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:battery-plus',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        BAT_DAILY_ENERGY_CHARGED
    ],
    'batdailyenergydischarged': [
        'Daily Energy Discharged',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:battery-minus',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        BAT_DAILY_ENERGY_DISCHARGED
    ],
    'griddailyongridenergy': [
        'Daily On-grid Energy',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_DAILY_ON_GRID_ENERGY
    ],
    'griddailyenergypurchased': [
        'Daily Grid Energy Purchased',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_DAILY_ENERGY_PURCHASED
    ],
    'griddailyenergyused': [
        'Daily Grid Energy Used',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_DAILY_ENERGY_USED
    ],
    'gridmonthlyenergypurchased': [
        'Monthly Grid Energy Purchased',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_MONTHLY_ENERGY_PURCHASED
    ],
    'gridmonthlyenergyused': [
        'Monthly Grid Energy Used',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_MONTHLY_ENERGY_USED
    ],
    'gridmontlyongridenergy': [
        'Monthly On-grid Energy',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_MONTHLY_ON_GRID_ENERGY
    ],
    'gridyearlyenergypurchased': [
        'Yearly Grid Energy Purchased',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_YEARLY_ENERGY_PURCHASED
    ],
    'gridyearlyenergyused': [
        'Yearly Grid Energy Used',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_YEARLY_ENERGY_USED
    ],
    'gridyearlyongridenergy': [
        'Yearly On-grid Energy',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_YEARLY_ON_GRID_ENERGY
    ],
    'gridtotalongridenergy': [
        'Total On-grid Energy',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_TOTAL_ON_GRID_ENERGY
    ],
    'gridtotalconsumptionenergy':[
        'Total Consumption Energy',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_TOTAL_CONSUMPTION_ENERGY
    ],
    'gridpowergridtotalpower': [
        'Power Grid total power',
        UnitOfPower.WATT,
        'mdi:home-export-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        GRID_TOTAL_POWER
    ],
    'gridtotalconsumptionpower': [
        'Total Consumption power',
        UnitOfPower.WATT,
        'mdi:home-import-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        GRID_TOTAL_CONSUMPTION_POWER
    ],
    'gridtotalenergypurchased': [
        'Total Energy Purchased',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_TOTAL_ENERGY_PURCHASED
    ],
    'gridtotalenergyused': [
        'Total Energy Used',
        UnitOfEnergy.KILO_WATT_HOUR,
        'mdi:transmission-tower',
        SensorDeviceClass.ENERGY,
        SensorStateClass.TOTAL_INCREASING,
        GRID_TOTAL_ENERGY_USED
    ],
    'gridphase1power': [
        'Grid Phase1 Power',
        UnitOfPower.WATT,
        'mdi:home-import-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        GRID_PHASE1_POWER
    ],
    'gridphase2power': [
        'Grid Phase2 Power',
        UnitOfPower.WATT,
        'mdi:home-import-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        GRID_PHASE2_POWER
    ],
    'gridphase3power': [
        'Grid Phase3 Power',
        UnitOfPower.WATT,
        'mdi:home-import-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        GRID_PHASE3_POWER
    ],
    'gridapparentphase1power': [
        'Grid Phase1 Apparent Power',
        UnitOfApparentPower.VOLT_AMPERE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_APPARENT_PHASE1_POWER
    ],
    'gridapparentphase2power': [
        'Grid Phase2 Apparent Power',
        UnitOfApparentPower.VOLT_AMPERE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_APPARENT_PHASE2_POWER
    ],
    'gridapparentphase3power': [
        'Grid Phase3 Apparent Power',
        UnitOfApparentPower.VOLT_AMPERE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_APPARENT_PHASE3_POWER
    ],
    'gridreactivephase1power': [
        'Grid Phase1 Reactive Power',
        POWER_VOLT_AMPERE_REACTIVE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_REACTIVE_PHASE1_POWER
    ],
    'gridreactivephase2power': [
        'Grid Phase2 Reactive Power',
        POWER_VOLT_AMPERE_REACTIVE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_REACTIVE_PHASE2_POWER
    ],
    'gridreactivephase3power': [
        'Grid Phase3 Reactive Power',
        POWER_VOLT_AMPERE_REACTIVE,
        'mdi:home-import-outline',
        None,
        SensorStateClass.MEASUREMENT,
        GRID_REACTIVE_PHASE3_POWER
    ],
    'planttotalconsumptionpower': [
        'Plant Total Consumption power',
        UnitOfPower.WATT,
        'mdi:home-import-outline',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        PLANT_TOTAL_CONSUMPTION_POWER
    ],
    'batstateofhealth': [
        'Battery State Of Health',
        PERCENTAGE,
        'mdi:battery',
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        BAT_STATE_OF_HEALTH
    ],
    'socChargingSet': [
        'Force Charge SOC',
        PERCENTAGE,
        'mdi:battery',
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        SOC_CHARGING_SET
    ],
    'socDischargeSet': [
        'Force Discharge SOC',
        PERCENTAGE,
        'mdi:battery',
        SensorDeviceClass.BATTERY,
        SensorStateClass.MEASUREMENT,
        SOC_DISCHARGE_SET
    ],
    'bypassloadpower': [
        'Backup Load Power',
        UnitOfPower.WATT,
        'mdi:battery-charging',
        SensorDeviceClass.POWER,
        SensorStateClass.MEASUREMENT,
        BYPASS_LOAD_POWER
    ],
    'meterItemACurrent': [
        'Meter item A current',
        UnitOfElectricCurrent.AMPERE,
        'mdi:home-import-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_A_CURRENT
    ],
    'meterItemAVoltage': [
        'Meter item A volt',
        UnitOfElectricPotential.VOLT,
        'mdi:home-import-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_A_VOLTAGE
    ],
    'meterItemBCurrent': [
        'Meter item B current',
        UnitOfElectricCurrent.AMPERE,
        'mdi:home-import-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_B_CURRENT
    ],
    'meterItemBVoltage': [
        'Meter item B volt',
        UnitOfElectricPotential.VOLT,
        'mdi:home-import-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_B_VOLTAGE
    ],
    'meterItemCCurrent': [
        'Meter item C current',
        UnitOfElectricCurrent.AMPERE,
        'mdi:home-import-outline',
        SensorDeviceClass.CURRENT,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_C_CURRENT
    ],
    'meterItemCVoltage': [
        'Meter item C volt',
        UnitOfElectricPotential.VOLT,
        'mdi:home-import-outline',
        SensorDeviceClass.VOLTAGE,
        SensorStateClass.MEASUREMENT,
        METER_ITEM_C_VOLTAGE
    ],
}

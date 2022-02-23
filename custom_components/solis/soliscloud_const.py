"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""
from .ginlong_const import *

# VERSION
VERSION = '0.1.1'

STRING_COUNT = 'dcStringCount'
STRING_LISTS = [
    [STRING1_CURRENT,STRING1_VOLTAGE,STRING1_POWER],
    [STRING2_CURRENT,STRING2_VOLTAGE,STRING2_POWER],
    [STRING3_CURRENT,STRING3_VOLTAGE,STRING3_POWER],
    [STRING4_CURRENT,STRING4_VOLTAGE,STRING4_POWER],
]
GRID_TOTAL_POWER_STR = 'gridTotalPowerUnit'
GRID_TOTAL_CONSUMPTION_POWER_STR = 'gridTotalConsumptionPowerUnit'
INVERTER_ACPOWER_STR = 'pacUnit'
GRID_TOTAL_ENERGY_USED_STR = 'homeLoadTotalEnergyUnit'
INVERTER_ENERGY_THIS_YEAR_STR = 'energyThisYearUnit'
INVERTER_ENERGY_TOTAL_LIFE_STR = 'energyTotalLifeUnit'
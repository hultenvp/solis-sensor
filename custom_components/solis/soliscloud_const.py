"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""
from .ginlong_const import *

# VERSION
VERSION = '0.1.6'

STRING_COUNT = 'dcStringCount'
STRING_LISTS = [
    [STRING1_CURRENT,STRING1_VOLTAGE,STRING1_POWER],
    [STRING2_CURRENT,STRING2_VOLTAGE,STRING2_POWER],
    [STRING3_CURRENT,STRING3_VOLTAGE,STRING3_POWER],
    [STRING4_CURRENT,STRING4_VOLTAGE,STRING4_POWER],
    [STRING5_CURRENT,STRING5_VOLTAGE,STRING5_POWER],
    [STRING6_CURRENT,STRING6_VOLTAGE,STRING6_POWER],
    [STRING7_CURRENT,STRING7_VOLTAGE,STRING7_POWER],
    [STRING8_CURRENT,STRING8_VOLTAGE,STRING8_POWER],
]
GRID_TOTAL_POWER_STR = 'gridTotalPowerUnit'
GRID_TOTAL_CONSUMPTION_POWER_STR = 'gridTotalConsumptionPowerUnit'
INVERTER_ACPOWER_STR = 'pacUnit'
GRID_TOTAL_ENERGY_USED_STR = 'homeLoadTotalEnergyUnit'
INVERTER_ENERGY_THIS_MONTH_STR = 'energyThisMonthUnit'
INVERTER_ENERGY_THIS_YEAR_STR = 'energyThisYearUnit'
INVERTER_ENERGY_TOTAL_LIFE_STR = 'energyTotalLifeUnit'
BAT_POWER_STR = 'batteryPowerUnit'
BAT_TOTAL_ENERGY_CHARGED_STR = 'batteryTotalChargeEnergyUnit'
BAT_TOTAL_ENERGY_DISCHARGED_STR = 'batteryTotalDischargeEnergyUnit'
BAT_CURRENT_STR = 'batteryCurrentUnit'
BAT_VOLTAGE_STR = 'batteryVoltageUnit'
GRID_TOTAL_ENERGY_PURCHASED_STR = 'totalEnergyPurchasedUnit'
GRID_DAILY_ON_GRID_ENERGY_STR = 'dailyOnGridEnergyUnit'
GRID_MONTHLY_ON_GRID_ENERGY_STR = 'monthlyOnGridEnergyUnit'
GRID_YEARLY_ON_GRID_ENERGY_STR = 'yearlyOnGridEnergyUnit'
GRID_TOTAL_ON_GRID_ENERGY_STR = 'totalOnGridEnergyUnit'
GRID_DAILY_ENERGY_PURCHASED_STR = 'dailyEnergyPurchasedUnit'
GRID_MONTHLY_ENERGY_PURCHASED_STR = 'monthlyEnergyPurchasedUnit'
GRID_YEARLY_ENERGY_PURCHASED_STR = 'yearlyEnergyPurchasedUnit'
GRID_DAILY_ENERGY_USED_STR = 'dailyEnergyUsedUnit'
BYPASS_LOAD_POWER_STR = 'bypassLoadPowerUnit'
PLANT_TOTAL_CONSUMPTION_POWER_STR = 'plantTotalConsumptionPowerUnit'

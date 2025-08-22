"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""

from .ginlong_const import *

# VERSION
VERSION = "0.1.8"

STRING_COUNT = "dcStringCount"
STRING_LISTS = []
for i in range(1,25):
    STRING_LISTS.append([
        globals()[f"STRING{i}_CURRENT"],
        globals()[f"STRING{i}_VOLTAGE"],
        globals()[f"STRING{i}_POWER"],
    ])
GRID_TOTAL_POWER_STR = "gridTotalPowerUnit"
GRID_TOTAL_CONSUMPTION_POWER_STR = "gridTotalConsumptionPowerUnit"
INVERTER_ACPOWER_STR = "pacUnit"
GRID_TOTAL_ENERGY_USED_STR = "homeLoadTotalEnergyUnit"
INVERTER_ENERGY_THIS_MONTH_STR = "energyThisMonthUnit"
INVERTER_ENERGY_THIS_YEAR_STR = "energyThisYearUnit"
INVERTER_ENERGY_TOTAL_LIFE_STR = "energyTotalLifeUnit"
BAT_POWER_STR = "batteryPowerUnit"
BAT_DAILY_ENERGY_CHARGED_STR = "batteryTodayChargeEnergyUnit"
BAT_DAILY_ENERGY_DISCHARGED_STR = "batteryTodayDischargeEnergyUnit"
BAT_MONTHLY_ENERGY_CHARGED_STR = "batteryMonthChargeEnergyUnit"
BAT_MONTHLY_ENERGY_DISCHARGED_STR = "batteryMonthDischargeEnergyUnit"
BAT_YEARLY_ENERGY_CHARGED_STR = "batteryYearChargeEnergyUnit"
BAT_YEARLY_ENERGY_DISCHARGED_STR = "batteryYearDischargeEnergyUnit"
BAT_TOTAL_ENERGY_CHARGED_STR = "batteryTotalChargeEnergyUnit"
BAT_TOTAL_ENERGY_DISCHARGED_STR = "batteryTotalDischargeEnergyUnit"
BAT_CURRENT_STR = "batteryCurrentUnit"
BAT_VOLTAGE_STR = "batteryVoltageUnit"
GRID_TOTAL_ENERGY_PURCHASED_STR = "totalEnergyPurchasedUnit"
GRID_DAILY_ON_GRID_ENERGY_STR = "dailyOnGridEnergyUnit"
GRID_MONTHLY_ON_GRID_ENERGY_STR = "monthlyOnGridEnergyUnit"
GRID_YEARLY_ON_GRID_ENERGY_STR = "yearlyOnGridEnergyUnit"
GRID_TOTAL_ON_GRID_ENERGY_STR = "totalOnGridEnergyUnit"
GRID_DAILY_ENERGY_PURCHASED_STR = "dailyEnergyPurchasedUnit"
GRID_MONTHLY_ENERGY_PURCHASED_STR = "monthlyEnergyPurchasedUnit"
GRID_YEARLY_ENERGY_PURCHASED_STR = "yearlyEnergyPurchasedUnit"
GRID_DAILY_ENERGY_USED_STR = "dailyEnergyUsedUnit"
BYPASS_LOAD_POWER_STR = "bypassLoadPowerUnit"
PLANT_TOTAL_CONSUMPTION_POWER_STR = "plantTotalConsumptionPowerUnit"

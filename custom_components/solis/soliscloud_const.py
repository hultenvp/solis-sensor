"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""

# VERSION
VERSION = "0.2.0"

STRING_LISTS = []
for i in range(1,25):
    globals()[f"STRING{i}_VOLTAGE"] = f"u_pv_{i}"
    globals()[f"STRING{i}_CURRENT"] = f"i_pv_{i}"
    globals()[f"STRING{i}_POWER"] = f"pow_{i}"
    STRING_LISTS.append([
        globals()[f"STRING{i}_CURRENT"],
        globals()[f"STRING{i}_VOLTAGE"],
        globals()[f"STRING{i}_POWER"],
    ])

STRING_COUNT = 'dc_inputtype'

INVERTER_SERIAL = 'sn'
INVERTER_PLANT_ID = 'station_id'
INVERTER_PLANT_NAME = 'station_name'
INVERTER_LAT = "lat"
INVERTER_LON = "lon"
INVERTER_ADDRESS = "address"
INVERTER_DEVICE_ID = 'id'
INVERTER_DATALOGGER_SERIAL = 'collectorsn'
INVERTER_TIMESTAMP_ONLINE = "timestampOnline"
INVERTER_TIMESTAMP_UPDATE = 'data_timestamp'
INVERTER_TEMPERATURE = 'inverter_temperature'
INVERTER_POWER_LIMIT = 'p_limit_set'
INVERTER_ACPOWER = 'pac'
INVERTER_ACFREQUENCY = 'fac'
#INVERTER_ENERGY_LAST_MONTH = 'e_month'
INVERTER_ENERGY_TODAY = 'e_today'
INVERTER_ENERGY_THIS_MONTH = 'e_month'
INVERTER_ENERGY_THIS_YEAR = 'e_year'
INVERTER_ENERGY_TOTAL_LIFE = 'e_total'
INVERTER_POWER_STATE = 'state'
INVERTER_STATE = 'state'
PHASE1_VOLTAGE = 'u_ac_1'
PHASE2_VOLTAGE = 'u_ac_2'
PHASE3_VOLTAGE = 'u_ac_3'
PHASE1_CURRENT = 'i_ac_1'
PHASE2_CURRENT = 'i_ac_2'
PHASE3_CURRENT = 'i_ac_3'
BAT_POWER = 'battery_power'
BAT_VOLTAGE = 'storage_battery_voltage'
BAT_CURRENT = 'storage_battery_current'
BAT_STATE_OF_HEALTH = 'battery_health_soh'
BAT_REMAINING_CAPACITY = 'battery_capacity_soc'
BAT_TOTAL_ENERGY_CHARGED = 'battery_total_charge_energy'
BAT_TOTAL_ENERGY_DISCHARGED = 'battery_total_discharge_energy'
BAT_DAILY_ENERGY_CHARGED = 'battery_today_charge_energy'
BAT_DAILY_ENERGY_DISCHARGED = 'battery_today_discharge_energy'
BAT_MONTHLY_ENERGY_CHARGED = 'battery_month_charge_energy'
BAT_MONTHLY_ENERGY_DISCHARGED = 'battery_month_discharge_energy'
BAT_YEARLY_ENERGY_CHARGED = 'battery_year_charge_energy'
BAT_YEARLY_ENERGY_DISCHARGED = 'battery_yesterday_charge_energy'
GRID_DAILY_ON_GRID_ENERGY = 'grid_sell_today_energy'
GRID_DAILY_ENERGY_PURCHASED = 'grid_purchased_today_energy'
GRID_DAILY_ENERGY_USED = 'home_load_today_energy'
GRID_MONTHLY_ENERGY_PURCHASED = 'grid_purchased_month_energy'
GRID_MONTHLY_ENERGY_USED = 'home_load_month_energy'
GRID_MONTHLY_ON_GRID_ENERGY = 'grid_sell_month_energy'
GRID_YEARLY_ENERGY_PURCHASED = 'grid_purchased_year_energy'
GRID_YEARLY_ENERGY_USED = 'home_load_year_energy'
GRID_YEARLY_ON_GRID_ENERGY = 'grid_sell_year_energy'
GRID_TOTAL_ON_GRID_ENERGY = 'grid_sell_total_energy'
GRID_TOTAL_CONSUMPTION_ENERGY = 'home_grid_total_energy'
GRID_TOTAL_POWER = 'psum'
GRID_TOTAL_CONSUMPTION_POWER = 'family_load_power'
GRID_TOTAL_ENERGY_PURCHASED = 'grid_purchased_total_energy'
GRID_TOTAL_ENERGY_USED = 'home_load_total_energy'
GRID_PHASE1_POWER = 'p_a'
GRID_PHASE2_POWER = 'p_b'
GRID_PHASE3_POWER = 'p_c'
GRID_APPARENT_PHASE1_POWER = 'a_looked_power'
GRID_APPARENT_PHASE2_POWER = 'b_looked_power'
GRID_APPARENT_PHASE3_POWER = 'c_looked_power'
GRID_REACTIVE_PHASE1_POWER = 'a_reactive_power'
GRID_REACTIVE_PHASE2_POWER = 'b_reactive_power'
GRID_REACTIVE_PHASE3_POWER = 'c_reactive_power'
SOC_CHARGING_SET = 'soc_charging_set'
SOC_DISCHARGE_SET = 'soc_discharge_set'
BYPASS_LOAD_POWER = 'bypass_load_power'
METER_ITEM_A_CURRENT = 'i_a'
METER_ITEM_A_VOLTAGE = 'u_a'
METER_ITEM_B_CURRENT = 'i_b'
METER_ITEM_B_VOLTAGE = 'u_b'
METER_ITEM_C_CURRENT = 'i_c'
METER_ITEM_C_VOLTAGE = 'u_c'
PLANT_TOTAL_CONSUMPTION_POWER = "plantTotalConsumptionPower"
HMI_VERSION_ALL = 'hmi_version_all'
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

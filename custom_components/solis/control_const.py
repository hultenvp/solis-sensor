from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.time import TimeEntityDescription
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from dataclasses import dataclass
from datetime import datetime
import logging

from .const import (
    DOMAIN,
    SERIAL,
    API_NAME,
    EMPTY_ATTR,
)

RETRIES = 1000
RETRY_WAIT = 10

HMI_CID = "6798"
_LOGGER = logging.getLogger(__name__)


class SolisBaseControlEntity:
    def __init__(self, service, config_name, inverter_sn, cid, info):
        self._measured: datetime | None = None
        self._entity_type = "control"
        self._attributes = dict(EMPTY_ATTR)
        self._attributes[SERIAL] = inverter_sn
        self._attributes[API_NAME] = service.api_name
        self._api = service.api
        self._platform_name = config_name
        self._name = f"{config_name.title()} {info.name}"
        self._key = f"{config_name}_{info.key}"
        self._inverter_sn = inverter_sn
        self._cid = cid
        self._splitter = ()
        self._index = 0
        self._joiner = ","

    @property
    def unique_id(self) -> str:
        return f"{self._platform_name}_{self._key}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def cid(self) -> int:
        return int(self._cid)

    @property
    def index(self) -> int:
        return self._index

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return a device description for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._attributes[SERIAL]}_{DOMAIN, self._attributes[API_NAME]}")},
            manufacturer=f"Solis {self._attributes[API_NAME]}",
            name=f"Solis_Inverter_{self._attributes[SERIAL]}",
        )

    async def write_control_data(self, value: str) -> bool:
        data = await self._api.write_control_data(self._attributes[SERIAL], self.cid, value)
        return data

    def split(self, value):
        if len(self._splitter) > 0:
            # if there's more than one split string then replace all of the later ones with the first before we split
            for x in self._splitter[1:]:
                value = value.replace(x, self._splitter[0])
            values = value.split(self._splitter[0])

            if self._index <= len(values):
                return values[self._index]
            else:
                _LOGGER.warning(f"Unable to retrieve item {self._index:d} from {value} for {self._key}")
        else:
            return value


@dataclass
class SolisSelectEntityDescription(SelectEntityDescription):
    option_dict: dict = None
    unit: type = float


@dataclass
class SolisNumberEntityDescription(NumberEntityDescription):
    splitter: tuple = ()


@dataclass
class SolisTimeEntityDescription(TimeEntityDescription):
    splitter: tuple = ()


@dataclass
class SolisButtonEntityDescription(ButtonEntityDescription):
    joiner: str = ","


# Control types dict[bool: dict] where key is HMI_4B00 flag

CONTROL_TYPES = {
    "time": SolisTimeEntityDescription,
    "number": SolisNumberEntityDescription,
    "select": SolisSelectEntityDescription,
    "button": SolisButtonEntityDescription,
}

ALL_CONTROLS = {
    True: {
        # 103 is still available with 4B00 but it doesn't do anything included here for testing only
        # "103": [
        #     SolisNumberEntityDescription(
        #         name="Timed Charge Current 1",
        #         key="timed_charge_current_1",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisNumberEntityDescription(
        #         name="Timed Discharge Current 1",
        #         key="timed_discharge_current_1",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge Start 1",
        #         key="timed_charge_start_1",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge End 1",
        #         key="timed_charge_end_1",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge Start 1",
        #         key="timed_discharge_start_1",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge End 1",
        #         key="timed_discharge_end_1",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisNumberEntityDescription(
        #         name="Timed Charge Current 2",
        #         key="timed_charge_current_2",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisNumberEntityDescription(
        #         name="Timed Discharge Current 2",
        #         key="timed_discharge_current_2",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge Start 2",
        #         key="timed_charge_start_2",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge End 2",
        #         key="timed_charge_end_2",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge Start 2",
        #         key="timed_discharge_start_2",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge End 2",
        #         key="timed_discharge_end_2",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisNumberEntityDescription(
        #         name="Timed Charge Current 3",
        #         key="timed_charge_current_3",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisNumberEntityDescription(
        #         name="Timed Discharge Current 3",
        #         key="timed_discharge_current_3",
        #         native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        #         device_class=SensorDeviceClass.CURRENT,
        #         icon="mdi:current-dc",
        #         native_min_value=0,
        #         native_max_value=100,
        #         native_step=1,
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge Start 3",
        #         key="timed_charge_start_3",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Charge End 3",
        #         key="timed_charge_end_3",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge Start 3",
        #         key="timed_discharge_start_3",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisTimeEntityDescription(
        #         name="Timed Discharge End 3",
        #         key="timed_discharge_end_3",
        #         icon="mdi:clock",
        #         splitter=(",", "-"),
        #     ),
        #     SolisButtonEntityDescription(
        #         name="Update Timed Charge/Discharge",
        #         key="update_timed_charge_discharge",
        #     ),
        # ],
        "157": [
            SolisNumberEntityDescription(
                name="Backup SOC",
                key="backup_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "158": [
            SolisNumberEntityDescription(
                name="Overdischarge SOC",
                key="overdischarge_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "160": [
            SolisNumberEntityDescription(
                name="Force Charge SOC",
                key="force_charge_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "636": [
            SolisSelectEntityDescription(
                name="Energy Storage Control Switch",
                key="energy_storage_control_switch",
                option_dict={
                    "1": "Self-Use - No Grid Charging",
                    "5": "Off-Grid Mode",
                    "9": "Battery Awaken - No Grid Charging",
                    "33": "Self-Use",
                    "41": "Battery Awaken",
                    "49": "Backup/Reserve",
                    "64": "Feed-in priority",
                },
                icon="mdi:dip-switch",
            )
        ],
        "5928": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 1",
                key="timed_charge_soc_1",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5948": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 1",
                key="timed_charge_current_1",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5946": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 1",
                key="timed_charge_start_1",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 1",
                key="timed_charge_end_1",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 1",
                key="update_timed_charge_1",
            ),
        ],
        "5965": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 1",
                key="timed_discharge_soc_1",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5967": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current 1",
                key="timed_discharge_current_1",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5964": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 1",
                key="timed_discharge_start_1",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 1",
                key="timed_discharge_end_1",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 1",
                key="update_timed_discharge_1",
            ),
        ],
        # ======================= Slot 2 =================================
        "5929": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 2",
                key="timed_charge_soc_2",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5951": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 2",
                key="timed_charge_current_2",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5949": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 2",
                key="timed_charge_start_2",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 2",
                key="timed_charge_end_2",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 2",
                key="update_timed_charge_2",
            ),
        ],
        "5969": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 2",
                key="timed_discharge_soc_2",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5971": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current",
                key="timed_discharge_current_2",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5968": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 2",
                key="timed_discharge_start_2",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 2",
                key="timed_discharge_end_2",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 2",
                key="update_timed_discharge_2",
            ),
        ],
        # ======================= Slot 3 =================================
        "5930": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 3",
                key="timed_charge_soc_3",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5954": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 3",
                key="timed_charge_current_3",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5952": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 3",
                key="timed_charge_start_3",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 3",
                key="timed_charge_end_3",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 3",
                key="update_timed_charge_3",
            ),
        ],
        "5973": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 3",
                key="timed_discharge_soc_3",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5975": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current 3",
                key="timed_discharge_current_3",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5972": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 3",
                key="timed_discharge_start_3",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 3",
                key="timed_discharge_end_3",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 3",
                key="update_timed_discharge_3",
            ),
        ],
        # ======================= Slot 4 =================================
        "5931": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 4",
                key="timed_charge_soc_4",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5957": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 4",
                key="timed_charge_current_4",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5955": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 4",
                key="timed_charge_start_4",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 4",
                key="timed_charge_end_4",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 4",
                key="update_timed_charge_4",
            ),
        ],
        "5977": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 4",
                key="timed_discharge_soc_4",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5979": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current 4",
                key="timed_discharge_current_4",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5976": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 4",
                key="timed_discharge_start_4",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 4",
                key="timed_discharge_end_4",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 4",
                key="update_timed_discharge_4",
            ),
        ],
        # ======================= Slot 5 =================================
        "5932": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 5",
                key="timed_charge_soc_5",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5960": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 5",
                key="timed_charge_current_5",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5958": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 5",
                key="timed_charge_start_5",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 5",
                key="timed_charge_end_5",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 5",
                key="update_timed_charge_5",
            ),
        ],
        "5981": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 5",
                key="timed_discharge_soc_5",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5983": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current 5",
                key="timed_discharge_current_5",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5980": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 5",
                key="timed_discharge_start_5",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 5",
                key="timed_discharge_end_5",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 5",
                key="update_timed_discharge_5",
            ),
        ],
        # ======================= Slot 6 =================================
        "5933": [
            SolisNumberEntityDescription(
                name="Timed Charge SOC 6",
                key="timed_charge_soc_6",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5963": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 6",
                key="timed_charge_current_6",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5961": [
            SolisTimeEntityDescription(
                name="Timed Charge Start 6",
                key="timed_charge_start_6",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 6",
                key="timed_charge_end_6",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge 6",
                key="update_timed_charge_6",
            ),
        ],
        "5984": [
            SolisNumberEntityDescription(
                name="Timed Discharge SOC 6",
                key="timed_discharge_soc_6",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5986": [
            SolisNumberEntityDescription(
                name="Timed Discharge Current 6",
                key="timed_discharge_current_6",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:battery-sync",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5987": [
            SolisTimeEntityDescription(
                name="Timed Discharge Start 6",
                key="timed_discharge_start_6",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 6",
                key="timed_discharge_end_6",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Discharge 6",
                key="update_timed_discharge_6",
            ),
        ],
    },
    False: {
        "103": [
            SolisNumberEntityDescription(
                name="Timed Charge Current 1",
                key="timed_charge_current_1",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisNumberEntityDescription(
                name="Timed Discharge Current 1",
                key="timed_discharge_current_1",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge Start 1",
                key="timed_charge_start_1",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 1",
                key="timed_charge_end_1",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge Start 1",
                key="timed_discharge_start_1",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 1",
                key="timed_discharge_end_1",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisNumberEntityDescription(
                name="Timed Charge Current 2",
                key="timed_charge_current_2",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisNumberEntityDescription(
                name="Timed Discharge Current 2",
                key="timed_discharge_current_2",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge Start 2",
                key="timed_charge_start_2",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 2",
                key="timed_charge_end_2",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge Start 2",
                key="timed_discharge_start_2",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 2",
                key="timed_discharge_end_2",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisNumberEntityDescription(
                name="Timed Charge Current 3",
                key="timed_charge_current_3",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisNumberEntityDescription(
                name="Timed Discharge Current 3",
                key="timed_discharge_current_3",
                native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
                device_class=SensorDeviceClass.CURRENT,
                icon="mdi:current-dc",
                native_min_value=0,
                native_max_value=100,
                native_step=1,
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge Start 3",
                key="timed_charge_start_3",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End 3",
                key="timed_charge_end_3",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge Start 3",
                key="timed_discharge_start_3",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Discharge End 3",
                key="timed_discharge_end_3",
                icon="mdi:clock",
                splitter=(",", "-"),
            ),
            SolisButtonEntityDescription(
                name="Update Timed Charge/Discharge",
                key="update_timed_charge_discharge",
            ),
        ],
        "157": [
            SolisNumberEntityDescription(
                name="Backup SOC",
                key="backup_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "158": [
            SolisNumberEntityDescription(
                name="Overdischarge SOC",
                key="overdischarge_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "160": [
            SolisNumberEntityDescription(
                name="Force Charge SOC",
                key="force_charge_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "636": [
            SolisSelectEntityDescription(
                name="Energy Storage Control Switch",
                key="energy_storage_control_switch",
                option_dict={
                    1: "Self-Use - No Grid Charging",
                    3: "Timed Charge/Discharge - No Grid Charging",
                    17: "Backup/Reserve - No Grid Charging",
                    33: "Self-Use - No Timed Charge/Discharge",
                    35: "Self-Use",
                    37: "Off-Grid Mode",
                    41: "Battery Awaken",
                    43: "Battery Awaken + Timed Charge/Discharge",
                    49: "Backup/Reserve - No Timed Charge/Discharge",
                    51: "Backup/Reserve",
                    64: "Feed-in priority - No Grid Charging",
                    96: "Feed-in priority - No Timed Charge/Discharge",
                    98: "Feed-in priority",
                },
                icon="mdi:dip-switch",
            )
        ],
    },
}

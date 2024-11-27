from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.time import TimeEntityDescription
from homeassistant.components.button import ButtonEntityDescription
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.entity import DeviceInfo
from dataclasses import dataclass
from datetime import datetime

from .const import (
    DOMAIN,
    LAST_UPDATED,
    SERIAL,
    API_NAME,
    EMPTY_ATTR,
)

RETRIES = 1000
RETRY_WAIT = 10

HMI_CID = "6798"


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
                value.replace(x, self._splitter[0])
            value = value.split(self._splitter[0])[self._index]
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

ALL_CONTROLS = {
    True: {
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
                name="Timed Charge SOC",
                key="timed_charge_soc",
                native_unit_of_measurement=PERCENTAGE,
                device_class=NumberDeviceClass.BATTERY,
                icon="mdi:battery-sync",
                native_min_value=10,
                native_max_value=100,
                native_step=1,
            )
        ],
        "5946": [
            SolisTimeEntityDescription(
                name="Timed Charge Start",
                key="timed_charge_start",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisTimeEntityDescription(
                name="Timed Charge End",
                key="timed_charge_end",
                icon="mdi:clock",
                splitter=("-"),
            ),
            SolisButtonEntityDescription(
                name="Timed Charge",
                key="timed_charge",
            ),
        ],
    },
    False: {
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
    },
}

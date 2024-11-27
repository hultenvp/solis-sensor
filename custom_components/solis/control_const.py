from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.number import NumberDeviceClass
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


class SolisBaseControlEntity:
    def __init__(self, service, config_name, inverter_sn, cid, info):
        self._measured: datetime | None = None
        self._entity_type = "control"
        self._attributes = dict(EMPTY_ATTR)
        self._attributes[SERIAL] = inverter_sn
        self._attributes[API_NAME] = service.api_name
        self._platform_name = config_name
        self._name = info.name
        self._key = info.key
        self._inverter_sn = inverter_sn
        self._cid = cid

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
    def device_info(self) -> DeviceInfo | None:
        """Return a device description for device registry."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._attributes[SERIAL]}_{DOMAIN, self._attributes[API_NAME]}")},
            manufacturer=f"Solis {self._attributes[API_NAME]}",
            name=f"Solis_Inverter_{self._attributes[SERIAL]}",
        )


@dataclass
class SolisSelectEntityDescription(SelectEntityDescription):
    cid: int = None
    option_dict: dict = None
    unit: type = float


@dataclass
class SolisNumberEntityDescription(NumberEntityDescription):
    cid: int = None


# Example usage
SELECT_TYPES = {
    "636": SolisSelectEntityDescription(
        name="Energy Storage Control Switch",
        key="energy_storage_control_switch",
        option_dict={
            1: "Self-Use - No Grid Charging",
            5: "Off-Grid Mode",
            9: "Battery Awaken - No Grid Charging",
            33: "Self-Use",
            41: "Battery Awaken",
            49: "Backup/Reserve",
            64: "Feed-in priority",
        },
        icon="mdi:dip-switch",
    ),
}

NUMBER_TYPES = {
    "5928": SolisNumberEntityDescription(
        name="Timed Charge SOC",
        key="timed_charge_soc",
        native_unit_of_measurement=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        icon="mdi:battery-sync",
        native_min_value=10,
        native_max_value=100,
        native_step=1,
    ),
}

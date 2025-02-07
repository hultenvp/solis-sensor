from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.time import TimeEntity


import asyncio
import logging
from datetime import datetime

from .const import (
    DOMAIN,
    LAST_UPDATED,
)

from .service import ServiceSubscriber, InverterService
from .control_const import SolisBaseControlEntity, RETRIES, RETRY_WAIT, ALL_CONTROLS, SolisTimeEntityDescription

_LOGGER = logging.getLogger(__name__)
RETRIES = 100
YEAR = 2024
MONTH = 1
DAY = 1


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Setup sensors from a config entry created in the integrations UI."""
    # Prepare the sensor entities.
    plant_id = config_entry.data["portal_plant_id"]
    _LOGGER.debug(f"config_entry.data: {config_entry.data}")
    _LOGGER.debug(f"Domain: {DOMAIN}")
    service = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.info(f"Waiting for discovery of controls for plant {plant_id}")
    await asyncio.sleep(8)
    attempts = 0
    while (attempts < RETRIES) and (not service.has_controls):
        _LOGGER.debug(f"    Attempt {attempts} failed")
        await asyncio.sleep(RETRY_WAIT)
        attempts += 1

    if service.has_controls:
        entities = []
        _LOGGER.debug(f"Plant ID {plant_id} has controls:")
        for inverter_sn in service.controls:
            for cid, index, entity, button, initial_value in service.controls[inverter_sn]["time"]:
                # service.set_active_times(inverter_sn, cid, index, (None, None)
                entities.append(
                    SolisTimeEntity(
                        service,
                        config_entry.data["name"],
                        inverter_sn,
                        cid,
                        entity,
                        index,
                        initial_value,
                    )
                )

        if len(entities) > 0:
            _LOGGER.debug(f"Creating {len(entities)} time entities")
            async_add_entities(entities)
        else:
            _LOGGER.debug(f"No time controls found for Plant ID {plant_id}")

    else:
        _LOGGER.debug(f"No time found for Plant ID {plant_id}")

    return True


class SolisTimeEntity(SolisBaseControlEntity, ServiceSubscriber, TimeEntity):
    def __init__(self, service: InverterService, config_name, inverter_sn, cid, time_info, index, initial_value):
        super().__init__(service, config_name, inverter_sn, cid, time_info)
        self._attr_native_value = datetime(
            year=YEAR,
            month=MONTH,
            day=DAY,
            hour=0,
            minute=0,
        ).time()
        self._icon = time_info.icon
        self._splitter = time_info.splitter
        self._index = index
        # self._active_times = service.active_times[inverter_sn]
        # Subscribe to the service with the cid as the index
        if initial_value is not None:
            self.do_update(initial_value, datetime.now())
        service.subscribe(self, inverter_sn, str(cid))

    def do_update(self, value, last_updated):
        # When the data from the API changes this method will be called with value as the new value
        # return super().do_update(value, last_updated)
        _LOGGER.debug(f"Update state for {self._name}")
        _LOGGER.debug(f">>> Initial value: {value}")
        values = self.split(value).split(":")
        _LOGGER.debug(f">>> Split value: {values}")
        time_value = None
        try:
            time_value = datetime(
                year=YEAR,
                month=MONTH,
                day=DAY,
                hour=int(values[0]),
                minute=int(values[1]),
            ).time()
            _LOGGER.debug(f">>> Datetime value: {time_value}")
        except:
            _LOGGER.debug("Unable to convert {value} to time")

        # Check if this time overlaps with any others

        if time_value is None:
            return False
        elif self.hass and self._attr_native_value != time_value:
            self._attr_native_value = time_value
            self._attributes[LAST_UPDATED] = last_updated
            self.async_write_ha_state()
            return True
        return False

    @property
    def to_string(self):
        return self._attr_native_value.strftime("%-H,%-M")

    async def async_set_value(self, value: float) -> None:
        _LOGGER.debug(f"async_set_value to {value} for {self._name}")
        self._attr_native_value = value
        self._attributes[LAST_UPDATED] = datetime.now()
        self.async_write_ha_state()
        # await self.write_control_data(str(value))

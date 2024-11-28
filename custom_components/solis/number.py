from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.number import NumberEntity


import asyncio
import logging
from datetime import datetime

from .const import (
    DOMAIN,
    LAST_UPDATED,
)

from .service import ServiceSubscriber, InverterService
from .control_const import SolisBaseControlEntity, RETRIES, RETRY_WAIT, ALL_CONTROLS, SolisNumberEntityDescription

_LOGGER = logging.getLogger(__name__)
RETRIES = 100


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Setup sensors from a config entry created in the integrations UI."""
    # Prepare the sensor entities.
    plant_id = config_entry.data["portal_plant_id"]
    _LOGGER.debug(f"config_entry.data: {config_entry.data}")
    _LOGGER.debug(f"Domain: {DOMAIN}")
    service = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.info(f"Waiting for discovery of Number entities for plant {plant_id}")
    await asyncio.sleep(8)
    attempts = 0
    while (attempts < RETRIES) and (not service.has_controls):
        _LOGGER.debug(f"    Attempt {attempts} failed")
        await asyncio.sleep(RETRY_WAIT)
        attempts += 1

    if service.has_controls:
        entities = []
        _LOGGER.debug(f"Plant ID {plant_id} has controls:")
        _LOGGER.debug(service.controls)
        for inverter_sn in service.controls:
            _LOGGER.debug(f"Waiting for inverter {inverter_sn} HMI status")
            attempts = 0
            while service.api._hmi_fb00[inverter_sn] is None:
                _LOGGER.debug(f"    Attempt {attempts} failed")
                await asyncio.sleep(RETRY_WAIT)
                attempts += 1
            hmi_fb00 = service.api._hmi_fb00[inverter_sn]
            _LOGGER.debug(f"Inverter SN {inverter_sn} HMI status {hmi_fb00}")
            for cid in service.controls[inverter_sn]:
                for index, entity in enumerate(ALL_CONTROLS[hmi_fb00][cid]):
                    if isinstance(entity, SolisNumberEntityDescription):
                        _LOGGER.debug(f"Adding number entity {entity.name} for inverter Sn {inverter_sn} cid {cid}")
                        entities.append(
                            SolisNumberEntity(
                                service,
                                config_entry.data["name"],
                                inverter_sn,
                                cid,
                                entity,
                                index,
                            )
                        )

        if len(entities) > 0:
            _LOGGER.debug(f"Creating {len(entities)} number entities")
            async_add_entities(entities)
        else:
            _LOGGER.debug(f"No number controls found for Plant ID {plant_id}")

    else:
        _LOGGER.debug(f"No controls found for Plant ID {plant_id}")

    return True


class SolisNumberEntity(SolisBaseControlEntity, ServiceSubscriber, NumberEntity):
    def __init__(self, service: InverterService, config_name, inverter_sn, cid, number_info, index):
        super().__init__(service, config_name, inverter_sn, cid, number_info)
        self._attr_native_value = 0
        self._attr_native_max_value = number_info.native_max_value
        self._attr_native_min_value = number_info.native_min_value
        self._attr_native_step = number_info.native_step
        self._attr_native_unit_of_measurement = number_info.native_unit_of_measurement
        self._icon = number_info.icon
        self._splitter = number_info.splitter
        self._index = index
        # Subscribe to the service with the cid as the index
        service.subscribe(self, inverter_sn, str(cid))

    def do_update(self, value, last_updated):
        # When the data from the API changes this method will be called with value as the new value
        # return super().do_update(value, last_updated)
        _LOGGER.debug(f"Update state for {self._name}")

        value = self.split(value)

        if self.hass and self._attr_native_value != value:
            self._attr_native_value = value
            self._attributes[LAST_UPDATED] = last_updated
            self.async_write_ha_state()
            return True
        return False

    def to_string(self):
        return str(self._attr_native_value)

    async def async_set_native_value(self, value: float) -> None:
        _LOGGER.debug(f"async_set_native_value for {self._name}")
        self._attr_native_value = value
        self._attributes[LAST_UPDATED] = datetime.now()
        self.async_write_ha_state()
        await self.write_control_data(str(value))

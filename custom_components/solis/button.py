from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.button import ButtonEntity


import asyncio
import logging
from datetime import datetime

from .const import (
    DOMAIN,
)

from .service import ServiceSubscriber, InverterService
from .control_const import SolisBaseControlEntity, RETRIES, RETRY_WAIT, ALL_CONTROLS, SolisButtonEntityDescription

_LOGGER = logging.getLogger(__name__)
RETRIES = 100


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities):
    """Setup sensors from a config entry created in the integrations UI."""
    # Prepare the sensor entities.
    plant_id = config_entry.data["portal_plant_id"]
    _LOGGER.debug(f"config_entry.data: {config_entry.data}")
    _LOGGER.debug(f"Domain: {DOMAIN}")
    service = hass.data[DOMAIN][config_entry.entry_id]

    _LOGGER.info(f"Waiting for discovery of Button entities for plant {plant_id}")
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
                _LOGGER.debug(f">>> {cid:4s}")
                for index, entity in enumerate(ALL_CONTROLS[hmi_fb00][cid]):
                    _LOGGER.debug(f">>>      {index} {entity.name} {isinstance(entity, SolisButtonEntityDescription)}")
                    if isinstance(entity, SolisButtonEntityDescription):
                        _LOGGER.debug(f"Adding Button entity {entity.name} for inverter Sn {inverter_sn} cid {cid}")
                        entities.append(
                            SolisButtonEntity(
                                service,
                                config_entry.data["name"],
                                inverter_sn,
                                cid,
                                entity,
                                index,
                            )
                        )

        if len(entities) > 0:
            _LOGGER.debug(f"Creating {len(entities)} Button entities")
            async_add_entities(entities)
        else:
            _LOGGER.debug(f"No Button controls found for Plant ID {plant_id}")

    else:
        _LOGGER.debug(f"No controls found for Plant ID {plant_id}")

    return True


class SolisButtonEntity(SolisBaseControlEntity, ServiceSubscriber, ButtonEntity):
    def __init__(self, service: InverterService, config_name, inverter_sn, cid, button_info, index):
        super().__init__(service, config_name, inverter_sn, cid, button_info)
        self._index = index
        self._joiner = button_info.joiner
        self._entities = service.subscriptions.get(inverter_sn, {}).get(cid, [])
        # Subscribe to the service with the cid as the index
        # service.subscribe(self, inverter_sn, str(cid))

    def do_update(self, value, last_updated):
        # When the data from the API changes this method will be called with value as the new value
        # return super().do_update(value, last_updated)
        pass

    async def async_press(self) -> None:
        """Handle the button press."""
        for entity in self._entities:
            _LOGGER.debug(f"{entity.name:s} {entity.to_string:s} {entity.index}")
        value = self. _joiner.join([entity.to_string for entity in self._entities])
        _LOGGER.debug(f"{self._cid} {value}")
        await self.write_control_data(value)
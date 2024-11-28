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
            for cid, index, entity, button, intial_value in service.controls[inverter_sn]["button"]:
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
        # Sort the entities by their index
        items = sorted({entity.index: entity.to_string for entity in self._entities}.items())
        value = self._joiner.join([x[1] for x in items])
        _LOGGER.debug(f"{self._cid} {value}")
        await self.write_control_data(value)

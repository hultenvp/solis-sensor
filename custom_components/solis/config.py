"""
Access to the Soliscloud API for PV monitoring.
Works for all Ginlong brands using the Soliscloud API

For more information: https://github.com/hultenvp/solis-sensor/
"""

from __future__ import annotations
import aiofiles
import async_timeout
import yaml

class SoliscloudConfig:
    """Portal configuration data"""

    def __init__(
        self,
        portal_domain: str,
        portal_username: str,
        portal_key_id: str,
        portal_secret: bytes,
        portal_plantid: str,
        portal_password: str,
    ) -> None:
        self._domain = portal_domain
        self._username = portal_username
        self._plant_id = portal_plantid
        self._key_id: str = portal_key_id
        self._secret: bytes = portal_secret
        self._workarounds = {}
        self._password: str = portal_password

    async def load_workarounds(self):
        try:
            async with aiofiles.open("/config/custom_components/solis/workarounds.yaml", "r") as file:
                content = await file.read()
                self._workarounds = yaml.safe_load(content)
                _LOGGER.debug("workarounds: %s", self._workarounds)
        except FileNotFoundError:
            pass

    @property
    def domain(self) -> str:
        """Configured portal domain name."""
        return self._domain

    @property
    def username(self) -> str:
        """Username."""
        return self._username

    @property
    def plant_id(self) -> str:
        """Configured plant ID."""
        return self._plant_id

    @property
    def key_id(self) -> str:
        """Key ID."""
        return self._key_id

    @property
    def secret(self) -> bytes:
        """API Key."""
        return self._secret

    @property
    def workarounds(self) -> dict[str, Any]:
        """Return all workaround settings"""
        return self._workarounds

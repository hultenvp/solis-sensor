"""Unit tests for last-known-good inverter list handling on login."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock


def _load_soliscloud_api():
    """Load soliscloud_api without importing Home Assistant-dependent package init."""
    if "solis.soliscloud_api" in sys.modules:
        return sys.modules["solis.soliscloud_api"]

    solis_dir = Path(__file__).resolve().parents[1] / "custom_components" / "solis"
    pkg = types.ModuleType("solis")
    pkg.__path__ = [str(solis_dir)]
    pkg.__package__ = "solis"
    sys.modules.setdefault("solis", pkg)

    def load(name: str, filename: str):
        spec = importlib.util.spec_from_file_location(f"solis.{name}", solis_dir / filename)
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "solis"
        sys.modules[f"solis.{name}"] = mod
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        return mod

    load("soliscloud_const", "soliscloud_const.py")
    load("ginlong_base", "ginlong_base.py")
    control = types.ModuleType("solis.control_const")
    control.ALL_CONTROLS = {}
    sys.modules["solis.control_const"] = control
    return load("soliscloud_api", "soliscloud_api.py")


_api_mod = _load_soliscloud_api()
SoliscloudAPI = _api_mod.SoliscloudAPI
SoliscloudApiError = _api_mod.SoliscloudApiError
SoliscloudConfig = _api_mod.SoliscloudConfig
SUCCESS = _api_mod.SUCCESS
CONTENT = _api_mod.CONTENT
STATUS_CODE = _api_mod.STATUS_CODE
MESSAGE = _api_mod.MESSAGE


class _PlantData:
    plantName = "Test Station"


def _config(plant_id: str = "plant-1") -> SoliscloudConfig:
    return SoliscloudConfig(
        "https://www.soliscloud.com:13333",
        "user",
        "keyid",
        b"secret",
        plant_id,
        "",
    )


class InverterListLastGoodTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        SoliscloudAPI._last_good_inverters = {}

    def tearDown(self) -> None:
        SoliscloudAPI._last_good_inverters = {}

    def _api(self, plant_id: str = "plant-1") -> SoliscloudAPI:
        api = SoliscloudAPI(_config(plant_id))
        api._config.load_workarounds = AsyncMock()
        return api

    async def test_successful_login_stores_last_good_list(self) -> None:
        api = self._api()
        api.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1", "SN2": "id2"})
        api.fetch_inverter_data = AsyncMock(return_value=_PlantData())

        self.assertTrue(await api.login(MagicMock()))
        self.assertEqual(api.inverters, {"SN1": "id1", "SN2": "id2"})
        self.assertEqual(SoliscloudAPI._last_good_inverters["plant-1"], {"SN1": "id1", "SN2": "id2"})

    async def test_partial_list_merges_last_known_inverters(self) -> None:
        SoliscloudAPI._last_good_inverters["plant-1"] = {
            "SN1": "id1",
            "SN2": "id2",
            "SN3": "id3",
            "SN4": "id4",
        }
        api = self._api()
        api.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1"})
        api.fetch_inverter_data = AsyncMock(return_value=_PlantData())

        self.assertTrue(await api.login(MagicMock()))
        self.assertEqual(set(api.inverters), {"SN1", "SN2", "SN3", "SN4"})
        self.assertEqual(api.inverters["SN4"], "id4")

    async def test_failed_list_uses_last_good_and_stays_online(self) -> None:
        SoliscloudAPI._last_good_inverters["plant-1"] = {"SN1": "id1", "SN2": "id2"}
        api = self._api()
        api.fetch_inverter_list = AsyncMock(side_effect=SoliscloudApiError("HTTP 502"))
        api.fetch_inverter_data = AsyncMock(return_value=_PlantData())

        self.assertTrue(await api.login(MagicMock()))
        self.assertEqual(api.inverters, {"SN1": "id1", "SN2": "id2"})
        self.assertTrue(api.is_online)

    async def test_failed_list_without_last_good_stays_offline(self) -> None:
        api = self._api()
        api.fetch_inverter_list = AsyncMock(side_effect=SoliscloudApiError("timeout"))

        self.assertFalse(await api.login(MagicMock()))
        self.assertFalse(api.is_online)
        self.assertEqual(api.inverters, {})

    async def test_details_fetch_failure_does_not_drop_inverter(self) -> None:
        api = self._api()
        api.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1", "SN2": "id2"})

        async def details(serial, controls=True):
            if serial == "SN2":
                return None
            return _PlantData()

        api.fetch_inverter_data = AsyncMock(side_effect=details)

        self.assertTrue(await api.login(MagicMock()))
        self.assertEqual(set(api.inverters), {"SN1", "SN2"})
        self.assertEqual(SoliscloudAPI._last_good_inverters["plant-1"]["SN2"], "id2")

    async def test_unknown_inverter_without_plant_name_is_removed(self) -> None:
        api = self._api()
        api.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1"})
        api.fetch_inverter_data = AsyncMock(return_value=object())

        self.assertTrue(await api.login(MagicMock()))
        self.assertEqual(api.inverters, {})
        self.assertNotIn("plant-1", SoliscloudAPI._last_good_inverters)

    async def test_last_good_survives_new_instance_reload(self) -> None:
        first = self._api()
        first.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1", "SN2": "id2"})
        first.fetch_inverter_data = AsyncMock(return_value=_PlantData())
        await first.login(MagicMock())

        reloaded = self._api()
        reloaded.fetch_inverter_list = AsyncMock(return_value={"SN1": "id1"})
        reloaded.fetch_inverter_data = AsyncMock(return_value=_PlantData())
        await reloaded.login(MagicMock())

        self.assertEqual(set(reloaded.inverters), {"SN1", "SN2"})

    async def test_last_good_is_isolated_per_plant(self) -> None:
        plant_a = self._api("plant-a")
        plant_a.fetch_inverter_list = AsyncMock(return_value={"SN-A": "id-a"})
        plant_a.fetch_inverter_data = AsyncMock(return_value=_PlantData())
        await plant_a.login(MagicMock())

        plant_b = self._api("plant-b")
        plant_b.fetch_inverter_list = AsyncMock(side_effect=SoliscloudApiError("HTTP 502"))

        self.assertFalse(await plant_b.login(MagicMock()))
        self.assertEqual(plant_a.inverters, {"SN-A": "id-a"})
        self.assertEqual(plant_b.inverters, {})

    async def test_unexpected_inverter_list_payload_is_an_error(self) -> None:
        api = self._api()
        api._post_data_json = AsyncMock(
            return_value={
                SUCCESS: True,
                CONTENT: {"code": "0", "data": None},
                STATUS_CODE: 200,
                MESSAGE: "OK",
            }
        )

        with self.assertRaises(SoliscloudApiError):
            await api.fetch_inverter_list("plant-1")


if __name__ == "__main__":
    unittest.main()

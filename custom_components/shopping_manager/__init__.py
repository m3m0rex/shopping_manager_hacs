"""The Shopping Manager integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ShoppingManagerApi
from .const import DOMAIN, PLATFORMS
from .coordinator import ShoppingManagerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    api = ShoppingManagerApi(
        entry.data["host"],
        entry.data.get("token") or None,
        session,
    )
    coordinator = ShoppingManagerCoordinator(
        hass, api, int(entry.data.get("scan_interval", 60))
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    # Register the shopping_manager.* services once (idempotent across entries)
    if not hass.services.has_service(DOMAIN, "create_list"):
        def _api_for_call(call):
            entry_id = call.data.get("config_entry")
            data = hass.data.get(DOMAIN, {})
            if entry_id and entry_id in data:
                return data[entry_id]["api"]
            first = next(iter(data.values()), None)
            if first:
                return first["api"]
            raise RuntimeError("Shopping Manager not configured")

        async def _refresh(call):
            entry_id = call.data.get("config_entry")
            data = hass.data.get(DOMAIN, {})
            targets = [data[entry_id]] if (entry_id and entry_id in data) else data.values()
            for inst in targets:
                coord = inst.get("coordinator")
                if coord:
                    await coord.async_request_refresh()

        async def _create_list(call):
            api = _api_for_call(call)
            name = call.data.get("name")
            if not name:
                _LOGGER.error("create_list: name required")
                return
            await api.create_list(name)
            await _refresh(call)

        async def _rename_list(call):
            api = _api_for_call(call)
            list_id = call.data.get("list_id")
            name = call.data.get("name")
            if not list_id or not name:
                _LOGGER.error("rename_list: list_id + name required")
                return
            await api.rename_list(int(list_id), name)
            await _refresh(call)

        async def _delete_list(call):
            api = _api_for_call(call)
            list_id = call.data.get("list_id")
            if not list_id:
                _LOGGER.error("delete_list: list_id required")
                return
            await api.delete_list(int(list_id))
            await _refresh(call)

        hass.services.async_register(DOMAIN, "create_list", _create_list)
        hass.services.async_register(DOMAIN, "rename_list", _rename_list)
        hass.services.async_register(DOMAIN, "delete_list", _delete_list)

    # Forward to platforms (todo) so the lists appear as HA todo entities
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok

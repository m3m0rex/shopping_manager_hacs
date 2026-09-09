"""Todo platform for Shopping Manager (native todo list in HA)."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]
    async_add_entities([ShoppingManagerTodoList(coordinator, api, entry)], True)


class ShoppingManagerTodoList(CoordinatorEntity, TodoListEntity):
    """A Shopping Manager todo list."""

    _attr_has_entity_name = True
    _attr_name = "Einkaufsliste"

    def __init__(self, coordinator, api, entry) -> None:
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_todo"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Shopping Manager",
            "manufacturer": "m3m0rex",
            "model": "Shopping Manager",
        }

    @property
    def todo_items(self) -> list[TodoItem]:
        items = (self.coordinator.data or {}).get("items", [])
        result = []
        for it in items:
            status = TodoItemStatus.COMPLETED if it["checked"] else TodoItemStatus.NEEDS_ACTION
            result.append(
                TodoItem(
                    summary=it["name"],
                    uid=str(it["id"]),
                    status=status,
                    description=it.get("quantity") or "",
                )
            )
        return result

    async def async_create_todo_item(self, item: TodoItem) -> None:
        await self._api.add_item(item.summary, quantity=item.description or "")
        await self.coordinator.async_request_refresh()

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        for uid in uids:
            try:
                await self._api.delete_item(int(uid))
            except (ValueError, TypeError):
                _LOGGER.warning("Ungültige UID %s", uid)
        await self.coordinator.async_request_refresh()

    async def async_update_todo_item(self, item: TodoItem) -> None:
        checked = item.status == TodoItemStatus.COMPLETED
        try:
            await self._api.set_checked(int(item.uid), checked)
        except (ValueError, TypeError):
            _LOGGER.warning("Ungültige UID %s", item.uid)
        await self.coordinator.async_request_refresh()

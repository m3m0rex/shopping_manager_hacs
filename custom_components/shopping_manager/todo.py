"""Todo platform for Shopping Manager (one HA todo list per shopping list)."""

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

    async def _refresh(now=None):
        await coordinator.async_request_refresh()

    # Build initial entities from the lists already present after first refresh
    data = coordinator.data or {}
    entities = []
    for list_id in data:
        entities.append(ShoppingManagerTodoList(coordinator, api, entry, list_id))
    async_add_entities(entities, True)

    # Track lists added/removed across refreshes and add new todo entities.
    seen = set(data.keys())

    @callback
    def _on_data_update():
        current = set((coordinator.data or {}).keys())
        for list_id in current - seen:
            async_add_entities([ShoppingManagerTodoList(coordinator, api, entry, list_id)], True)
        seen.clear()
        seen.update(current)

    coordinator.async_add_listener(_on_data_update)


class ShoppingManagerTodoList(CoordinatorEntity, TodoListEntity):
    """One Shopping Manager list shown as a HA todo list."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, api, entry, list_id) -> None:
        super().__init__(coordinator)
        self._api = api
        self._entry = entry
        self._list_id = list_id
        self._attr_unique_id = f"{entry.entry_id}_list_{list_id}"

    @property
    def name(self) -> str:
        lst = (self.coordinator.data or {}).get(self._list_id, {})
        return lst.get("name", f"Liste {self._list_id}")

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
        lst = (self.coordinator.data or {}).get(self._list_id, {})
        result = []
        for it in lst.get("items", []):
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
        await self._api.add_item_to_list(self._list_id, item.summary, quantity=item.description or "")
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

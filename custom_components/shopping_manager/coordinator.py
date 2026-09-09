"""DataUpdateCoordinator for Shopping Manager (multi-list)."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, InvalidAuth, ShoppingManagerApi

_LOGGER = logging.getLogger(__name__)


class ShoppingManagerCoordinator(DataUpdateCoordinator):
    """Coordinate fetching of shopping lists; one entry per list."""

    def __init__(self, hass: HomeAssistant, api: ShoppingManagerApi, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="shopping_manager",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self):
        try:
            lists = await self.api.get_lists()
        except InvalidAuth as err:
            raise UpdateFailed(f"Auth fehlgeschlagen: {err}") from err
        except ApiError as err:
            raise UpdateFailed(f"API-Fehler: {err}") from err

        result = {}
        for lst in lists:
            list_id = lst.get("id")
            try:
                items = await self.api.get_items_for_list(list_id)
            except (ApiError, InvalidAuth):
                items = []
            normalized = []
            for it in items:
                normalized.append({
                    "id": it.get("id"),
                    "list_id": list_id,
                    "name": it.get("name", ""),
                    "quantity": it.get("quantity", ""),
                    "checked": bool(it.get("checked")),
                    "source": it.get("source", "manual"),
                    "note": it.get("note") or "",
                    "image_url": it.get("image_url"),
                    "external_url": it.get("external_url"),
                    "sort_order": it.get("sort_order", 0),
                })
            result[list_id] = {
                "id": list_id,
                "name": lst.get("name", f"Liste {list_id}"),
                "is_owner": bool(lst.get("is_owner")),
                "items": normalized,
            }
        return result

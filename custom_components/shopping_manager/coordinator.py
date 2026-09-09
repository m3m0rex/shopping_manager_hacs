"""DataUpdateCoordinator for Shopping Manager."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, InvalidAuth, ShoppingManagerApi

_LOGGER = logging.getLogger(__name__)


class ShoppingManagerCoordinator(DataUpdateCoordinator):
    """Coordinate fetching of shopping list items."""

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
            items = await self.api.get_items()
            counts = await self.api.get_counts()
        except InvalidAuth as err:
            raise UpdateFailed(f"Auth fehlgeschlagen: {err}") from err
        except ApiError as err:
            raise UpdateFailed(f"API-Fehler: {err}") from err
        # Normalize: ensure consistent keys
        normalized = []
        for it in items:
            normalized.append({
                "id": it.get("id"),
                "name": it.get("name", ""),
                "quantity": it.get("quantity", ""),
                "checked": bool(it.get("checked")),
                "source": it.get("source", "manual"),
                "note": it.get("note") or "",
                "image_url": it.get("image_url"),
                "external_url": it.get("external_url"),
                "sort_order": it.get("sort_order", 0),
            })
        return {"items": normalized, "counts": counts}

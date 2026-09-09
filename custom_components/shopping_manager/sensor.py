"""Sensor platform for Shopping Manager (aggregated counts across all lists)."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities(
        [
            ShoppingManagerOpenSensor(coordinator, entry),
            ShoppingManagerCheckedSensor(coordinator, entry),
            ShoppingManagerTotalSensor(coordinator, entry),
        ],
        True,
    )


class _Base(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Shopping Manager",
            "manufacturer": "m3m0rex",
            "model": "Shopping Manager",
        }

    def _counts(self):
        # Aggregate across all lists held by the coordinator
        data = self.coordinator.data or {}
        open_c = checked_c = 0
        for lst in data.values():
            for it in lst.get("items", []):
                if it["checked"]:
                    checked_c += 1
                else:
                    open_c += 1
        return {"open": open_c, "checked": checked_c, "total": open_c + checked_c}


class ShoppingManagerOpenSensor(_Base):
    _attr_translation_key = "open_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return self._counts()["open"]


class ShoppingManagerCheckedSensor(_Base):
    _attr_translation_key = "checked_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return self._counts()["checked"]


class ShoppingManagerTotalSensor(_Base):
    _attr_translation_key = "total_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return self._counts()["total"]

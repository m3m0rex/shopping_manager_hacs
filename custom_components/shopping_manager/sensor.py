"""Sensor platform for Shopping Manager."""

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


class ShoppingManagerOpenSensor(_Base):
    _attr_translation_key = "open_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("counts", {}).get("open", 0)


class ShoppingManagerCheckedSensor(_Base):
    _attr_translation_key = "checked_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("counts", {}).get("checked", 0)


class ShoppingManagerTotalSensor(_Base):
    _attr_translation_key = "total_count"
    _attr_native_unit_of_measurement = "items"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("counts", {}).get("total", 0)

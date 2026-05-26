from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AionFluxCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator: AionFluxCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        AionFluxOnlineSensor(coordinator, device_id)
        for device_id in coordinator.data
    )


class AionFluxOnlineSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: AionFluxCoordinator, device_id: str) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        dev = coordinator.data[device_id]
        slug = dev["dev_eui"]
        self._attr_unique_id = f"aionflux_{slug}_online"
        self._attr_name = f"{dev['name']} Online"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, slug)},
            name=dev["name"],
            manufacturer="AionFlux",
            model="LoRaWAN Sensor",
            configuration_url=coordinator.api_url,
        )

    @property
    def is_on(self) -> bool:
        device = self.coordinator.data.get(self._device_id)
        return bool(device and device.get("is_online", False))

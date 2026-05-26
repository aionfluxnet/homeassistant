from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AionFluxCoordinator

# (key, source, name, unit, device_class, state_class, icon)
SENSOR_TYPES: list[tuple] = [
    ("temperature",  "telemetry", "Temperature",     UnitOfTemperature.CELSIUS,       SensorDeviceClass.TEMPERATURE,     SensorStateClass.MEASUREMENT,        "mdi:thermometer"),
    ("humidity",     "telemetry", "Humidity",        PERCENTAGE,                      SensorDeviceClass.HUMIDITY,        SensorStateClass.MEASUREMENT,        "mdi:water-percent"),
    ("range",        "telemetry", "Range",           "mm",                            SensorDeviceClass.DISTANCE,        SensorStateClass.MEASUREMENT,        "mdi:ruler"),
    ("battery_mv",   "telemetry", "Battery Voltage", UnitOfElectricPotential.MILLIVOLT, SensorDeviceClass.VOLTAGE,       SensorStateClass.MEASUREMENT,        "mdi:battery"),
    ("interval_min", "telemetry", "Uplink Interval", "min",                           None,                              SensorStateClass.MEASUREMENT,        "mdi:timer-outline"),
    ("uptime_sec",   "telemetry", "Uptime",          UnitOfTime.SECONDS,              SensorDeviceClass.DURATION,        SensorStateClass.TOTAL_INCREASING,   "mdi:clock-outline"),
    ("last_rssi",    "device",    "RSSI",            "dBm",                           SensorDeviceClass.SIGNAL_STRENGTH, SensorStateClass.MEASUREMENT,        "mdi:signal"),
    ("last_snr",     "device",    "SNR",             "dB",                            None,                              SensorStateClass.MEASUREMENT,        "mdi:signal-variant"),
    ("active_alerts","alerts",    "Active Alerts",   None,                            None,                              SensorStateClass.MEASUREMENT,        "mdi:alert-circle"),
]


def _get_value(device: dict, key: str, source: str):
    if source == "telemetry":
        return device.get("telemetry", {}).get(key)
    if source == "device":
        return device.get(key)
    if source == "alerts":
        return len(device.get("active_alerts", []))
    return None


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> None:
    coordinator: AionFluxCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for device_id, device in coordinator.data.items():
        for sensor_def in SENSOR_TYPES:
            key, source = sensor_def[0], sensor_def[1]
            if _get_value(device, key, source) is not None:
                entities.append(AionFluxSensor(coordinator, device_id, sensor_def))
    async_add_entities(entities)


class AionFluxSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: AionFluxCoordinator,
        device_id: str,
        sensor_def: tuple,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        (
            self._key,
            self._source,
            name_suffix,
            unit,
            device_class,
            state_class,
            icon,
        ) = sensor_def

        dev = coordinator.data[device_id]
        slug = dev["dev_eui"]

        self._attr_unique_id = f"aionflux_{slug}_{self._key}"
        self._attr_name = f"{dev['name']} {name_suffix}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_icon = icon
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, slug)},
            name=dev["name"],
            manufacturer="AionFlux",
            model="LoRaWAN Sensor",
            configuration_url=coordinator.api_url,
        )

    @property
    def native_value(self):
        device = self.coordinator.data.get(self._device_id)
        if device is None:
            return None
        return _get_value(device, self._key, self._source)

    @property
    def extra_state_attributes(self) -> dict | None:
        if self._key != "active_alerts":
            return None
        device = self.coordinator.data.get(self._device_id)
        if not device:
            return None
        alerts = device.get("active_alerts", [])
        if not alerts:
            return None
        return {
            "alerts": [
                {
                    "rule": a["rule_name"],
                    "severity": a["severity"],
                    "message": a["message"],
                }
                for a in alerts
            ]
        }

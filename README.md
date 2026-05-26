# AionFlux — Home Assistant Integration

Integrates [AionFlux](https://aionflux.net) IoT platform devices as entities in Home Assistant.

## Features

- **Sensors** per device: temperature, humidity, distance (range), battery voltage, RSSI, SNR, uplink interval, uptime, active alert count
- **Binary sensor**: online/offline connectivity status
- **Automatic polling** — configurable interval (10–300 s, default 30 s)
- **HACS** compatible

## Installation via HACS

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/aionfluxnet/homeassistant` as category **Integration**
3. Search for **AionFlux** and install
4. Restart Home Assistant

## Manual installation

Copy `custom_components/aionflux/` to your HA `config/custom_components/` directory and restart.

## Configuration

1. Generate an API key in AionFlux → **Settings → Integrations**
2. In HA: **Settings → Devices & Services → Add Integration → AionFlux**
3. Enter:
   - **API URL**: `https://api.aionflux.net` (or your self-hosted instance)
   - **API Key**: the key generated above
   - **Update interval**: how often to poll (seconds)

## Entities

For each enrolled AionFlux device, the following entities are created (only if the device reports that field):

| Entity | Type | Unit |
|--------|------|------|
| Temperature | Sensor | °C |
| Humidity | Sensor | % |
| Range | Sensor | mm |
| Battery Voltage | Sensor | mV |
| RSSI | Sensor | dBm |
| SNR | Sensor | dB |
| Uplink Interval | Sensor | min |
| Uptime | Sensor | s |
| Active Alerts | Sensor | count |
| Online | Binary Sensor | — |

All entities are grouped under a HA Device per AionFlux device, identified by `dev_eui`.

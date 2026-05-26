# AionFlux

Integrates [AionFlux](https://aionflux.net) IoT platform devices as entities in Home Assistant.

## Features

- **Sensors** per device: temperature, humidity, distance (range), battery voltage, RSSI, SNR, uplink interval, uptime, active alert count
- **Binary sensor**: online/offline connectivity status
- **Automatic polling** — configurable interval (10–300 s, default 30 s)

## Configuration

1. Generate an API key in AionFlux → **Settings → Integrations**
2. In HA: **Settings → Devices & Services → Add Integration → AionFlux**
3. Enter the API URL and the generated API key

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AionFluxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, api_url: str, api_key: str, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                f"{self.api_url}/api/integrations/ha/devices",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status == 401:
                    raise UpdateFailed("Invalid API key")
                if response.status != 200:
                    raise UpdateFailed(f"API returned {response.status}")
                data = await response.json()
                return {d["id"]: d for d in data.get("devices", [])}
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error: {err}") from err

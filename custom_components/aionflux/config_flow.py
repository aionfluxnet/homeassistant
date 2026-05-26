import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_API_URL, DEFAULT_SCAN_INTERVAL, DOMAIN


class AionFluxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_url = user_input["api_url"].rstrip("/")
            api_key = user_input["api_key"].strip()
            session = async_get_clientsession(self.hass)
            try:
                async with session.get(
                    f"{api_url}/api/integrations/ha/devices",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 401:
                        errors["api_key"] = "invalid_auth"
                    elif response.status != 200:
                        errors["base"] = "cannot_connect"
                    else:
                        await self.async_set_unique_id(api_url)
                        self._abort_if_unique_id_configured()
                        return self.async_create_entry(
                            title="AionFlux",
                            data={
                                "api_url": api_url,
                                "api_key": api_key,
                                "scan_interval": user_input.get("scan_interval", DEFAULT_SCAN_INTERVAL),
                            },
                        )
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_url", default=DEFAULT_API_URL): str,
                    vol.Required("api_key"): str,
                    vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
                        int, vol.Range(min=10, max=300)
                    ),
                }
            ),
            errors=errors,
        )

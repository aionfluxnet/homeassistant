import logging
import ssl
import urllib.error
import urllib.request

import voluptuous as vol
from homeassistant import config_entries

from .const import DEFAULT_API_URL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _check_api(api_url: str, api_key: str) -> int:
    """Run a blocking HTTP check. Returns HTTP status code, or -1 on error."""
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        f"{api_url}/api/integrations/ha/devices",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception as exc:
        _LOGGER.error("AionFlux connection check failed [%s]: %s", type(exc).__name__, exc)
        return -1


class AionFluxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_url = user_input["api_url"].rstrip("/")
            api_key = user_input["api_key"].strip()

            status = await self.hass.async_add_executor_job(_check_api, api_url, api_key)

            if status == 200:
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
            elif status == 401:
                errors["api_key"] = "invalid_auth"
            else:
                _LOGGER.error("AionFlux API returned HTTP %s", status)
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

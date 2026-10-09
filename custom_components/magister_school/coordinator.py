import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import issue_registry as ir

from .api import MagisterAPI, AuthenticationRequired
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MagisterDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator voor Magister data updates."""

    def __init__(self, hass: HomeAssistant, school: str, username: str, password: str, totp_secret: str = None, days_back: int = 0, days_forward: int = 14, history_file: str = None, *, entry: ConfigEntry):
        self.api = MagisterAPI(school, username, password, totp_secret=totp_secret, days_back=days_back, days_forward=days_forward, history_file=history_file)
        self._entry_title = entry.title
        self._issue_id = f"fetch_failed_{entry.entry_id}"
        entry.async_on_unload(lambda: ir.async_delete_issue(hass, DOMAIN, self._issue_id))
        
        super().__init__(
            hass,
            _LOGGER,
            name="Magister",
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(self.api.get_data)
            if not data.get("kinderen"):
                raise UpdateFailed("No student data returned by Magister")
            ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
            _LOGGER.debug("Magister data succesvol opgehaald")
            return data
        except AuthenticationRequired as err:
            _LOGGER.error("Authenticatie vereist voor Magister: %s", err)
            persistent_notification.async_create(
                self.hass,
                "Mogelijk nieuw wachtwoord of onjuiste 2FA-sleutel voor Magister. Ga naar Configuratie → Integrations → Magister om opnieuw in te loggen.",
                title="Magister - Re-authentication required",
            )
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            ir.async_create_issue(
                self.hass, DOMAIN, self._issue_id,
                is_fixable=False, is_persistent=False, severity=ir.IssueSeverity.ERROR,
                translation_key="fetch_failed",
                translation_placeholders={"name": self._entry_title, "error": str(err)},
            )
            raise UpdateFailed(f"Error communicating with Magister API: {err}") from err

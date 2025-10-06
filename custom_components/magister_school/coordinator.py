import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .api import MagisterAPI

_LOGGER = logging.getLogger(__name__)

class MagisterDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator voor Magister data updates."""

    def __init__(self, hass: HomeAssistant, school: str, username: str, password: str):
        self.api = MagisterAPI(school, username, password)
        
        super().__init__(
            hass,
            _LOGGER,
            name="Magister",
            update_interval=timedelta(minutes=15),
        )

    async def _async_update_data(self):
        try:
            data = await self.hass.async_add_executor_job(self.api.get_data)
            _LOGGER.debug("Magister data succesvol opgehaald")
            return data
        except Exception as err:
            _LOGGER.error("Fout bij ophalen Magister data: %s", err)
            raise UpdateFailed(f"Error communicating with Magister API: {err}")

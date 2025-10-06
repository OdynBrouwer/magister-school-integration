import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def validate_input(hass, data):
    """Valideer de gebruikersinvoer."""
    school = data["school"]
    user = data["user"]
    password = data["pass"]

    # TODO: Hier moet jouw echte Magister login/test functie komen
    if not school or not user or not password:
        raise ValueError("invalid_auth")

    return {
        "title": f"Magister - {school}",
        "user": user,
    }

class MagisterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor Magister integratie."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                await self.async_set_unique_id(f"{user_input['school']}_{user_input['user']}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

            except ValueError as err:
                if str(err) == "invalid_auth":
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "unknown"
            except Exception as err:
                _LOGGER.exception("Onverwachte fout: %s", err)
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required("school"): str,
                vol.Required("user"): str,
                vol.Required("pass"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MagisterOptionsFlow(config_entry)

class MagisterOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema(
            {
                vol.Optional("poll_interval", default=self.config_entry.options.get("poll_interval", 300)): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=options_schema,
            errors=errors,
        )

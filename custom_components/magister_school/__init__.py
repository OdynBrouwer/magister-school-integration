"""Magister School integration setup."""

import json
import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DEFAULT_POLL_INTERVAL, DOMAIN
from .coordinator import MagisterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CARD_FILENAME = "magister-school-card.js"
CARD_URL = f"/{DOMAIN}/{CARD_FILENAME}"
PLATFORMS = ["sensor", "calendar"]


def _card_version() -> str:
    """Return the integration version, used to bust the browser cache."""
    try:
        manifest = json.loads(
            (Path(__file__).parent / "manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return "0"
    return str(manifest.get("version", "0"))


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the bundled Lovelace card and register it as a dashboard resource."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get("card_static_registered"):
        www_dir = Path(__file__).parent / "www"
        if not (www_dir / CARD_FILENAME).is_file():
            _LOGGER.debug("Bundled Magister card not found, skipping registration")
            return
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL, str(www_dir / CARD_FILENAME), False)]
        )
        domain_data["card_static_registered"] = True

    resources = getattr(hass.data.get(LOVELACE_DATA), "resources", None)
    if resources is None or not hasattr(resources, "async_create_item"):
        _LOGGER.debug("Lovelace resources unavailable, not registering card")
        return

    if not getattr(resources, "loaded", True):
        await resources.async_get_info()

    if any(
        str(item.get("url", "")).startswith(CARD_URL)
        for item in resources.async_items()
    ):
        return

    try:
        await resources.async_create_item(
            {"res_type": "module", "url": f"{CARD_URL}?v={_card_version()}"}
        )
    except Exception as err:  # noqa: BLE001 - a failed resource must not break setup
        _LOGGER.warning("Could not register Magister card resource: %s", err)


async def _async_migrate_unique_ids(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Prefix existing unique IDs with the entry ID, keeping entity IDs intact.

    Unique IDs used to be global, so two accounts could collide and Home
    Assistant appended ``_1`` suffixes to the entity IDs.
    """
    registry = er.async_get(hass)
    prefix = f"{entry.entry_id}_"

    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        unique_id = entity.unique_id
        if not unique_id or unique_id.startswith(prefix):
            continue
        try:
            registry.async_update_entity(
                entity.entity_id, new_unique_id=f"{prefix}{unique_id}"
            )
        except Exception as err:  # noqa: BLE001 - never block setup on migration
            _LOGGER.debug(
                "Could not migrate unique ID for %s: %s", entity.entity_id, err
            )


async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Magister from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = MagisterDataUpdateCoordinator(
        hass,
        entry.entry_id,
        entry.data["school"],
        entry.data["user"],
        entry.data["pass"],
        totp_secret=entry.data.get("totp_secret"),
        days_back=entry.options.get("dagen_terug", 0),
        days_forward=entry.options.get("dagen_vooruit", 14),
        poll_interval=entry.options.get("poll_interval", DEFAULT_POLL_INTERVAL),
        history_file=hass.config.path(
            ".storage", "magister_school_appointment_history.json"
        ),
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    entry.async_on_unload(entry.add_update_listener(_async_update_options))

    await coordinator.async_config_entry_first_refresh()

    await _async_migrate_unique_ids(hass, entry)
    await _async_register_card(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS
    ):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

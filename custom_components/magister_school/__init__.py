import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .coordinator import MagisterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Suffixes die we willen opruimen
SUFFIXES_TO_CLEAN = ["_1", "_2", "_3", "_4", "_5"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Magister from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create coordinator
    coordinator = MagisterDataUpdateCoordinator(
        hass,
        entry.data["school"],
        entry.data["user"],
        entry.data["pass"]
    )

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Cleanup entities with suffixes (e.g. after HACS update)
    await _cleanup_suffix_entities(hass)

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor","calendar"])

    return True

async def _cleanup_suffix_entities(hass: HomeAssistant):
    """Hernoem entities met _1, _2, etc. suffixes als het doel-ID vrij is."""
    registry = er.async_get(hass)
    entities_to_cleanup = []

    # Scan alle entities die met 'sensor.magister_' beginnen
    for entity_id in list(registry.entities.keys()):
        if not (entity_id.startswith(("sensor.magister_", "calendar.magister_"))):
            continue

        cleaned_id = None
        for suffix in SUFFIXES_TO_CLEAN:
            if entity_id.endswith(suffix):
                candidate = entity_id[:-len(suffix)]
                # Alleen hernoemen als het doel nog niet bestaat
                if candidate not in registry.entities:
                    cleaned_id = candidate
                    break

        if cleaned_id:
            entities_to_cleanup.append((entity_id, cleaned_id))

    if not entities_to_cleanup:
        _LOGGER.debug("Geen Magister-entities met suffixes gevonden voor cleanup.")
        return

    _LOGGER.info("Hernoem %d Magister-entities met suffixes...", len(entities_to_cleanup))
    success_count = 0

    for old_id, new_id in entities_to_cleanup:
        try:
            registry.async_update_entity(old_id, new_entity_id=new_id)
            _LOGGER.debug("Hernoemd: %s -> %s", old_id, new_id)
            success_count += 1
        except Exception as e:
            _LOGGER.warning("Kon %s niet hernoemen naar %s: %s", old_id, new_id, e)

    # Toon melding als er iets is gedaan
    if success_count > 0:
        await hass.services.async_call(
            "persistent_notification",
            "create",
            {
                "title": "Magister School - Automatische Cleanup",
                "message": f"✅ {success_count} entities met suffixes (zoals _1, _2) zijn automatisch hernoemd.",
                "notification_id": "magister_school_suffix_cleanup"
            },
            blocking=False
        )

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, ["sensor","calendar"]):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

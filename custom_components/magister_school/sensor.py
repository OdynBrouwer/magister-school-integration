# sensor.py
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DEFAULT_NAME
from .coordinator import MagisterDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback
):
    """Set up Magister sensor from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    # Wacht op eerste data update VOOR we sensors maken
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()
    
    sensors = [MagisterMainSensor(coordinator, DEFAULT_NAME)]
    
    # Create individuele sensors voor elk kind
    if coordinator.data and "kinderen" in coordinator.data:
        for kind_naam in coordinator.data["kinderen"]:
            sensors.extend(create_kind_sensors(coordinator, kind_naam))
    
    async_add_entities(sensors, update_before_add=False)

def create_kind_sensors(coordinator, kind_naam):
    """Maak alle individuele sensors aan voor een kind."""
    base_id = kind_naam.lower().replace(' ', '_')
    
    return [
        # Overview sensor voor templates (deze moet erbij!)
        KindOverviewSensor(coordinator, kind_naam, base_id),
        
        # Basis info sensors
        KindAantalAfsprakenSensor(coordinator, kind_naam, base_id),
        KindAantalHuiswerkSensor(coordinator, kind_naam, base_id),
        KindVolgendeAfspraakSensor(coordinator, kind_naam, base_id),
        
        # Detail sensors
        KindCijfersSensor(coordinator, kind_naam, base_id),
        KindAfsprakenSensor(coordinator, kind_naam, base_id),
        KindRoosterWijzigingenSensor(coordinator, kind_naam, base_id),
        KindOpdrachtenSensor(coordinator, kind_naam, base_id),
        KindAbsentiesSensor(coordinator, kind_naam, base_id),
        KindStudiewijzersSensor(coordinator, kind_naam, base_id),
        KindActiviteitenSensor(coordinator, kind_naam, base_id),
        KindAanmeldingenSensor(coordinator, kind_naam, base_id),
    ]

class KindOverviewSensor(SensorEntity):
    """Sensor met overzicht van alle data voor templates."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_overview"
        self._attr_name = f"Magister {kind_naam}"
        self._attr_icon = "mdi:school"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        return kind_data.get("aantal_afspraken_vandaag", 0) if kind_data else 0

    @property
    def extra_state_attributes(self):
        """Return ALLE data voor templates."""
        kind_data = self._get_kind_data()
        if not kind_data:
            return {}

        attributes = {
            "naam": kind_data.get("naam"),
            "stamnummer": kind_data.get("stamnummer"),
            "geboortedatum": kind_data.get("geboortedatum"),
            "aanmeldingen": kind_data.get("aanmeldingen", []),
            "afspraken": kind_data.get("afspraken", []),
            "wijzigingen": kind_data.get("wijzigingen", []),
            "aantal_afspraken_vandaag": kind_data.get("aantal_afspraken_vandaag", 0),
            "aantal_huiswerk": kind_data.get("aantal_huiswerk", 0),
            "volgende_afspraak": kind_data.get("volgende_afspraak", "Geen"),
            "volgende_vak": kind_data.get("volgende_vak", ""),
        }

        # Voeg extra data toe
        for data_type in ["cijfers", "opdrachten", "absenties", "studiewijzers", "activiteiten"]:
            if data_type in self._coordinator.data and self._kind_naam in self._coordinator.data[data_type]:
                attributes[data_type] = self._coordinator.data[data_type][self._kind_naam]

        return attributes

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

class MagisterMainSensor(SensorEntity):
    """Hoofd sensor met alle Magister data."""

    def __init__(self, coordinator, name):
        self._coordinator = coordinator
        self._name = name
        self._attr_unique_id = "magister_main_data"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        """Return de laatste update tijd."""
        if self._coordinator.data:
            return self._coordinator.data.get("last_update", "unknown")
        return "unavailable"

    @property
    def extra_state_attributes(self):
        """Return alle data als attributes."""
        return self._coordinator.data or {}

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


# Basis Kind Sensors
class KindAantalAfsprakenSensor(SensorEntity):
    """Sensor voor aantal afspraken vandaag."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_afspraken_vandaag"
        self._attr_name = f"Magister {kind_naam} Afspraken Vandaag"
        self._attr_icon = "mdi:calendar-today"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        return kind_data.get("aantal_afspraken_vandaag", 0) if kind_data else 0

    @property
    def extra_state_attributes(self):
        kind_data = self._get_kind_data()
        return {
            "kind_naam": self._kind_naam,
            "afspraken_vandaag": kind_data.get("afspraken", []) if kind_data else []
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindAantalHuiswerkSensor(SensorEntity):
    """Sensor voor aantal huiswerk items."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_huiswerk"
        self._attr_name = f"Magister {kind_naam} Huiswerk"
        self._attr_icon = "mdi:book-education"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        return kind_data.get("aantal_huiswerk", 0) if kind_data else 0

    @property
    def extra_state_attributes(self):
        return {
            "kind_naam": self._kind_naam,
            "huiswerk_items": self._coordinator.data.get("opdrachten", {}).get(self._kind_naam, []) if self._coordinator.data else []
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindVolgendeAfspraakSensor(SensorEntity):
    """Sensor voor volgende afspraak."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_volgende_afspraak"
        self._attr_name = f"Magister {kind_naam} Volgende Afspraak"
        self._attr_icon = "mdi:clock-outline"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        return kind_data.get("volgende_afspraak", "Geen") if kind_data else "Geen"

    @property
    def extra_state_attributes(self):
        kind_data = self._get_kind_data()
        return {
            "kind_naam": self._kind_naam,
            "volgende_vak": kind_data.get("volgende_vak", "") if kind_data else ""
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


# Detail Sensors
class KindCijfersSensor(SensorEntity):
    """Sensor voor cijfers overzicht."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_cijfers"
        self._attr_name = f"Magister {kind_naam} Cijfers"
        self._attr_icon = "mdi:certificate"

    @property
    def state(self):
        if not self._coordinator.data:
            return 0
        cijfers = self._coordinator.data.get("cijfers", {}).get(self._kind_naam, [])
        return len(cijfers)

    @property
    def extra_state_attributes(self):
        if not self._coordinator.data:
            return {"kind_naam": self._kind_naam, "cijfers": [], "laatste_3_cijfers": []}
        
        cijfers = self._coordinator.data.get("cijfers", {}).get(self._kind_naam, [])
        return {
            "kind_naam": self._kind_naam,
            "cijfers": cijfers,
            "laatste_3_cijfers": cijfers[-3:] if cijfers else []
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindAfsprakenSensor(SensorEntity):
    """Sensor voor alle afspraken."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_afspraken"
        self._attr_name = f"Magister {kind_naam} Afspraken"
        self._attr_icon = "mdi:calendar"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        afspraken = kind_data.get("afspraken", []) if kind_data else []
        return len(afspraken)

    @property
    def extra_state_attributes(self):
        kind_data = self._get_kind_data()
        return {
            "kind_naam": self._kind_naam,
            "afspraken": kind_data.get("afspraken", []) if kind_data else [],
            "afspraken_vandaag": kind_data.get("aantal_afspraken_vandaag", 0) if kind_data else 0
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindRoosterWijzigingenSensor(SensorEntity):
    """Sensor voor roosterwijzigingen."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_wijzigingen"
        self._attr_name = f"Magister {kind_naam} Roosterwijzigingen"
        self._attr_icon = "mdi:calendar-alert"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        wijzigingen = kind_data.get("wijzigingen", []) if kind_data else []
        return len(wijzigingen)

    @property
    def extra_state_attributes(self):
        kind_data = self._get_kind_data()
        return {
            "kind_naam": self._kind_naam,
            "wijzigingen": kind_data.get("wijzigingen", []) if kind_data else []
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindOpdrachtenSensor(SensorEntity):
    """Sensor voor opdrachten."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_opdrachten"
        self._attr_name = f"Magister {kind_naam} Opdrachten"
        self._attr_icon = "mdi:clipboard-list"

    @property
    def state(self):
        if not self._coordinator.data:
            return 0
        opdrachten = self._coordinator.data.get("opdrachten", {}).get(self._kind_naam, [])
        return len(opdrachten)

    @property
    def extra_state_attributes(self):
        if not self._coordinator.data:
            return {"kind_naam": self._kind_naam, "opdrachten": [], "open_opdrachten": []}
        
        opdrachten = self._coordinator.data.get("opdrachten", {}).get(self._kind_naam, [])
        return {
            "kind_naam": self._kind_naam,
            "opdrachten": opdrachten,
            "open_opdrachten": [o for o in opdrachten if not o.get("ingeleverd_op")]
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindAbsentiesSensor(SensorEntity):
    """Sensor voor absenties."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_absenties"
        self._attr_name = f"Magister {kind_naam} Absenties"
        self._attr_icon = "mdi:account-clock"

    @property
    def state(self):
        if not self._coordinator.data:
            return 0
        absenties = self._coordinator.data.get("absenties", {}).get(self._kind_naam, [])
        return len(absenties)

    @property
    def extra_state_attributes(self):
        if not self._coordinator.data:
            return {"kind_naam": self._kind_naam, "absenties": [], "recente_absenties": []}
        
        absenties = self._coordinator.data.get("absenties", {}).get(self._kind_naam, [])
        return {
            "kind_naam": self._kind_naam,
            "absenties": absenties,
            "recente_absenties": absenties[-5:] if absenties else []
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindStudiewijzersSensor(SensorEntity):
    """Sensor voor studiewijzers."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_studiewijzers"
        self._attr_name = f"Magister {kind_naam} Studiewijzers"
        self._attr_icon = "mdi:book-open-variant"

    @property
    def state(self):
        if not self._coordinator.data:
            return 0
        studiewijzers = self._coordinator.data.get("studiewijzers", {}).get(self._kind_naam, [])
        return len(studiewijzers)

    @property
    def extra_state_attributes(self):
        if not self._coordinator.data:
            return {"kind_naam": self._kind_naam, "studiewijzers": []}
        
        studiewijzers = self._coordinator.data.get("studiewijzers", {}).get(self._kind_naam, [])
        return {
            "kind_naam": self._kind_naam,
            "studiewijzers": studiewijzers
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindActiviteitenSensor(SensorEntity):
    """Sensor voor activiteiten."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_activiteiten"
        self._attr_name = f"Magister {kind_naam} Activiteiten"
        self._attr_icon = "mdi:calendar-star"

    @property
    def state(self):
        if not self._coordinator.data:
            return 0
        activiteiten = self._coordinator.data.get("activiteiten", {}).get(self._kind_naam, [])
        return len(activiteiten)

    @property
    def extra_state_attributes(self):
        if not self._coordinator.data:
            return {"kind_naam": self._kind_naam, "activiteiten": []}
        
        activiteiten = self._coordinator.data.get("activiteiten", {}).get(self._kind_naam, [])
        return {
            "kind_naam": self._kind_naam,
            "activiteiten": activiteiten
        }

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )


class KindAanmeldingenSensor(SensorEntity):
    """Sensor voor aanmeldingen."""
    
    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}_aanmeldingen"
        self._attr_name = f"Magister {kind_naam} Aanmeldingen"
        self._attr_icon = "mdi:school"

    @property
    def state(self):
        kind_data = self._get_kind_data()
        aanmeldingen = kind_data.get("aanmeldingen", []) if kind_data else []
        return len(aanmeldingen)

    @property
    def extra_state_attributes(self):
        kind_data = self._get_kind_data()
        return {
            "kind_naam": self._kind_naam,
            "aanmeldingen": kind_data.get("aanmeldingen", []) if kind_data else []
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return self._coordinator.last_update_success and self._get_kind_data() is not None

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

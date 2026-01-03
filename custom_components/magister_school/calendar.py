import copy
from datetime import date, datetime, timedelta
import logging
from typing import cast
from zoneinfo import ZoneInfo

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Magister sensor from config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Wacht op eerste data update VOOR we sensors maken
    if not coordinator.data:
        await coordinator.async_config_entry_first_refresh()

    calendars = []

    # Create individuele kalender voor elk kind
    if coordinator.data and "kinderen" in coordinator.data:
        for kind_naam in coordinator.data["kinderen"]:
            base_id = kind_naam.lower().replace(" ", "_")
            calendars.append(KindKalenderSensor(coordinator, kind_naam, base_id))

    async_add_entities(calendars, update_before_add=False)


def _parse_dt(value: str | None) -> datetime | None:
    """Parse ISO datetime string to a timezone-aware datetime, or return None if value is missing."""

    if not value:
        return None

    parsed_dt = datetime.fromisoformat(value)

    # Ensure timezone info (use Amsterdam as default)
    tz = ZoneInfo("Europe/Amsterdam")
    if parsed_dt.tzinfo is None:
        parsed_dt = parsed_dt.replace(tzinfo=tz)
    else:
        parsed_dt = parsed_dt.astimezone(tz)
    return parsed_dt


def _create_calendar_event(afspraak: dict) -> CalendarEvent:
    """Create a CalendarEvent from an afspraak dict."""

    start_dt = _parse_dt(afspraak.get("start"))
    end_dt = _parse_dt(afspraak.get("einde"))

    if start_dt is None or end_dt is None:
        raise ValueError("Afspraak missing start or einde datetime")

    return CalendarEvent(
        start=start_dt,
        end=end_dt,
        summary=afspraak.get("omschrijving", "Afspraak"),
        description=afspraak.get("inhoud", ""),
        location=afspraak.get("lokaal", ""),
    )


def _event_duration_seconds(event: CalendarEvent) -> float:
    """Return event duration in seconds, handling date or datetime types."""
    tz = ZoneInfo("Europe/Amsterdam")
    start = event.start
    end = event.end

    # Normalize date-only values to datetime at midnight in the configured timezone
    if isinstance(start, date) and not isinstance(start, datetime):
        start = datetime(start.year, start.month, start.day, tzinfo=tz)
    if isinstance(end, date) and not isinstance(end, datetime):
        end = datetime(end.year, end.month, end.day, tzinfo=tz)

    # If we still don't have datetimes, treat duration as zero
    if not isinstance(start, datetime) or not isinstance(end, datetime):
        return 0.0

    delta = end - start
    return max(delta.total_seconds(), 0.0)


class KindKalenderSensor(CalendarEntity):
    """Sensor voor alle afspraken."""

    def __init__(self, coordinator, kind_naam, base_id):
        self._coordinator = coordinator
        self._kind_naam = kind_naam
        self._attr_unique_id = f"magister_{base_id}"
        self._attr_name = f"Magister {kind_naam} Kalender"
        self._attr_icon = "mdi:calendar"

    @property
    def extra_state_attributes(self):
        return {
            "kind_naam": self._kind_naam,
        }

    def _get_kind_data(self):
        if not self._coordinator.data:
            return None
        return self._coordinator.data.get("kinderen", {}).get(self._kind_naam)

    @property
    def event(self) -> CalendarEvent | None:
        """Return de volgende kalender event."""

        current_events = self._get_events(dt_util.now(), dt_util.now())
        if current_events:
            # Sort by latest start first, then by shortest duration
            current_events.sort(key=lambda e: e.start, reverse=True)
            current_events.sort(key=_event_duration_seconds)
            return current_events[0]

        next_events = self._get_events(
            dt_util.now(), datetime.max.replace(tzinfo=ZoneInfo("Europe/Amsterdam"))
        )
        return next_events[0] if next_events else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return kalender events binnen de gegeven datums."""
        return self._get_events(start_date, end_date)

    def _get_events(
        self, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        kind_data = self._get_kind_data()
        if not kind_data:
            return []

        events: list[CalendarEvent] = []
        for afspraak in kind_data.get("afspraken", []):
            try:
                event = _create_calendar_event(afspraak)
            except ValueError:
                # Skip events with invalid/missing datetime fields
                continue

            if event.start is None or event.end is None:
                continue

            start_dt: datetime = cast(datetime, event.start)
            end_dt: datetime = cast(datetime, event.end)

            # if event in interval
            if start_dt <= end_date and end_dt >= start_date:
                if end_dt.date() == start_dt.date():
                    events.append(event)
                else:
                    # If the afspraak spans multiple days, expand it into a repeating daily event for each day in the span using the same start/end times.
                    segment_start = start_dt
                    while segment_start <= end_dt:
                        segment_end = end_dt.replace(
                            year=segment_start.year,
                            month=segment_start.month,
                            day=segment_start.day,
                        )
                        if segment_start <= end_date and segment_end >= start_date:
                            segment_event = copy.copy(event)
                            segment_event.rrule = "FREQ=DAILY"
                            segment_event.start = segment_start
                            segment_event.end = segment_end
                            events.append(segment_event)

                        segment_start = segment_start + timedelta(days=1)

        # Sort events by start datetime and duration (shortest event first), then by start time
        events.sort(key=lambda e: (e.start, _event_duration_seconds(e)))

        return events

    @property
    def should_poll(self):
        return False

    @property
    def available(self):
        return (
            self._coordinator.last_update_success and self._get_kind_data() is not None
        )

    async def async_update(self):
        await self._coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

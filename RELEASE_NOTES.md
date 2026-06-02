# Release v2.0.1

## GitHub release text

Magister School Integration v2.0.1 adds agenda data to the overview sensor, making it directly available to the Magister School Card and other custom dashboards.

### What's new in v2.0.x

- Agenda calendar support via `calendar.py` (v2.0.0).
- Improved appointment handling in `script/magister.py` (v2.0.0).
- Five new agenda sensors per child (v2.0.0).
- **New in v2.0.1**: Overview sensor now includes agenda attributes:
  - `school_start_vandaag`, `school_einde_vandaag` (HH:MM, or "Geen")
  - `volgende_schooldag` (YYYY-MM-DD, or "Geen")
  - `volgende_schooldag_start`, `volgende_schooldag_einde` (HH:MM, or "Geen")
  - `lessen_vandaag` (array with start, einde, vak, omschrijving, lokaal)

### Fixes

- Renamed agenda sensor classes for consistency (v2.0.0).
- All-day/midnight items filtered so sensors show real times instead of `00:00`.

## HACS update text

This release adds agenda data to the overview sensor, making it directly available for cards and dashboards. All agenda sensors already present since v2.0.0.

## PR summary

- **PR 9**: agenda calendar support via `calendar.py`.
- **PR 10**: improved `script/magister.py` data handling.
- **PR 17**: five new agenda sensors per child.
- **Fix**: class names corrected to `Schooldag`; entity IDs stayed unchanged.
- **v2.0.1**: agenda attributes added to overview sensor.
# Release v2.0.3

## GitHub release text

Magister School Integration v2.0.3 is a maintenance release that prepares the integration for the official HACS repository.

### What's new in v2.0.3

- Added a HACS + hassfest validation workflow (`.github/workflows/validate.yml`).
- Added the required `issue_tracker` to `manifest.json`.
- Added brand assets (`brand/icon.png`) so the integration gets a proper icon in HACS.
- Removed unused `entity` translations with invalid `{kind}` keys (fixes hassfest).
- Sorted `manifest.json` keys to satisfy hassfest.

There are no changes to sensors or runtime behaviour in this release.

## HACS update text

Maintenance release: HACS and hassfest validation now pass, a brand icon was added, and the integration is prepared for the official HACS repository.

## Previous release: v2.0.2

# Release v2.0.2

## GitHub release text

Magister School Integration v2.0.2 improves error handling when the Magister subprocess times out.

### Fixes

- Prevented subprocess timeout exceptions from exposing the full command line, including credentials, in Home Assistant logs.
- Kept the existing Magister and 2FA login flow unchanged.

## HACS update text

This release improves timeout error handling so credentials are not included in the resulting Home Assistant log message.

## Previous release: v2.0.1

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
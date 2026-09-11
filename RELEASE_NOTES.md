# Release v2.0.5

## GitHub release text

Magister School Integration v2.0.5 fixes two remaining 2FA login issues and moves the roster-change history into the Home Assistant config directory.

### Fixes

- **2FA login (#34)**: the `pairfidopromo` step no longer discards the username/password/session fields, and the soft-token challenge now also accepts the `softtoken` action spelling used by some Magister tenants.
- **Login diagnostics**: login failures now write a message to stderr in JSON mode, so Home Assistant logs show a real cause instead of an empty JSON error.
- **Roster-change history (#35)**: the `was_afwijkend` history is now stored under `/config/.storage` instead of the container home, so it survives Core updates and is included in backups.

## HACS update text

Fixes the remaining 2FA login issues (pairfidopromo payload and the softtoken spelling), improves login error reporting, and stores the roster-change history under /config so it survives updates and is backed up.

## Previous release: v2.0.4

## GitHub release text

Magister School Integration v2.0.4 fixes the reported 2FA, date-window, homework and roster-change issues, and moves credentials out of the command line.

### Fixes

- **TOTP / 2FA (#34)**: the soft-token challenge now posts the `Code` field, and the TOTP secret is passed through from the config entry to the script.
- **Configurable date window (#32)**: new `dagen_terug` / `dagen_vooruit` options (defaults 0 / 14), validated as non-negative and applied immediately when changed.
- **Homework (#31)**: the homework sensor now shows unfinished homework, with `aantal_huiswerk_totaal`, `aantal_huiswerk_afgerond` and `aantal_huiswerk_onafgerond` attributes. Matching uses subject name and code.
- **Roster changes / uitval (#33)**: `was_afwijkend` is remembered so a lesson stays marked as changed even after Magister overwrites `Status` with `In Gebruik` or `Afgesloten`.

### Security

- Credentials (username, password and TOTP secret) are now passed via environment variables instead of command-line arguments, so they no longer appear in process listings or timeout logs (#23).

## HACS update text

Fixes 2FA/TOTP login, adds a configurable date window, improves homework and roster-change handling, and keeps credentials out of the command line.

## Previous release: v2.0.3

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
# Release v2.0.0

## GitHub release text

Magister School Integration v2.0.0 adds agenda calendar support, improved appointment handling, and five new agenda sensors per child.

### Highlights

- Added the agenda calendar from PR 9.
- Improved appointment and schedule data handling from PR 10.
- Added five agenda sensors per child from PR 17.
- Renamed the agenda sensor classes for consistency.
- Ignored all-day/midnight items so the sensors show real times instead of `00:00`.

## HACS update text

This release adds agenda calendar support, better appointment handling, and five new agenda sensors per child. It also fixes the agenda sensor naming and filters out all-day/midnight items so the sensor states show correct times.

## PR summary

- **PR 9**: agenda calendar support via `calendar.py`.
- **PR 10**: improved `script/magister.py` data handling.
- **PR 17**: five new agenda sensors per child.
- **Fix**: class names corrected to `Schooldag`; entity IDs stayed unchanged.
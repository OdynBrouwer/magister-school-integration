# Forum/community post

> Draft for publication in the international Home Assistant forum.

---

**Title:** Magister (NL) – blueprints for cancelled lessons, homework, grades, absences and schedule changes

Hi everyone,

I created two blueprints for the Magister integration (`magister_school`) so
you can receive notifications without editing any YAML:

- **Magister - notification on change** – cancelled lessons, new homework,
  new grades, new absences and schedule changes. Choose the notification type
  for each automation; the blueprint handles the rest.
- **Magister - daily overview** – a summary of the school day at a time of
  your choice: number of appointments, start/end time, next subject and the
  number of outstanding homework assignments.

Features:

- only **new** items trigger a notification (deduplicated per type, so there
  are no repeated notifications on every refresh);
- **no** notification spam after restarting Home Assistant;
- supports multiple children (select the overview sensor for each child);
- optional `input_boolean` master and per-notification-type switches;
- notifications through `notify.send_message` (Companion app), Home Assistant
  2024.8 or newer.

Import:

- Notification on change:

  [![Open the blueprint import dialog in Home Assistant.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_melding.yaml)
- Daily overview:

  [![Open the blueprint import dialog in Home Assistant.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_dagoverzicht.yaml)

Note: a blueprint cannot create helpers. If you want to use switches, add the
optional package to `config/packages/`, or leave the switch fields empty and
use the automation's enabled/disabled toggle.

Feedback and improvements are welcome!

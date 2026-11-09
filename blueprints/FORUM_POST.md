# Forum-/communitypost (concept)

> Concept voor publicatie. Vertaal naar het Engels als je in het internationale
> HA-forum post.

---

**Titel:** Magister (NL) – blueprints voor lesuitval, huiswerk, cijfers, absenties en roosterwijzigingen

Hoi allemaal,

Voor de Magister-integratie (`magister_school`) heb ik twee blueprints gemaakt,
zodat je meldingen kunt krijgen zonder YAML aan te passen:

- **Magister - melding bij wijziging** – lesuitval, nieuw huiswerk, nieuwe
  cijfers, nieuwe absenties en roosterwijzigingen. Je kiest per automation het
  type; de blueprint regelt de rest.
- **Magister - dagelijks overzicht** – elke schooldag op een zelfgekozen tijd
  een samenvatting: aantal afspraken, begin-/eindtijd, eerstvolgende vak en het
  aantal open huiswerkopdrachten.

Wat erin zit:

- alleen **nieuwe** items geven een melding (dedupe per type, dus geen
  herhalingen bij elke verversing);
- **geen** push-spam na een herstart van Home Assistant;
- werkt per kind (je kiest de overzichtsensor);
- optionele `input_boolean` als hoofdschakelaar en per meldingstype;
- meldingen via `notify.send_message` (Companion-app), HA 2024.8+.

Importeren:

- Melding bij wijziging: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_melding.yaml
- Dagelijks overzicht: https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_dagoverzicht.yaml

Let op: een blueprint kan géén helpers aanmaken. Wil je schakelaars gebruiken,
zet dan het optionele package in `config/packages/`, of laat de schakelaarvelden
leeg en gebruik de aan/uit-schakelaar van de automation.

Feedback en verbeteringen zijn welkom!

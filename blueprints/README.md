# Magister – meldingen voor Home Assistant

Blueprints voor de integratie `magister_school` (Magister in Home Assistant). Je
krijgt pushmeldingen bij **lesuitval**, **nieuw huiswerk**, **nieuwe cijfers**,
**nieuwe absenties**, **roosterwijzigingen** en **nieuwe berichten of
mededelingen**, plus een optioneel **dagelijks overzicht** van de schooldag.

Je hoeft niets in YAML aan te passen: je kiest je Magister-sensor en je
notify-entiteit in de gebruikersinterface.

---

## Wat krijg je

| Blueprint | Wat het doet |
|---|---|
| `magister_melding.yaml` | Eén blueprint voor de 5 gebeurtenis-meldingen; je kiest per automation het type. Maak dus **één automation per meldingstype**. |
| `magister_berichten.yaml` | Melding bij een **nieuw bericht** of een **nieuwe mededeling** van school, inclusief onderwerp en afzender. |
| `magister_dagoverzicht.yaml` | Stuurt op gekozen dagen op een gekozen tijdstip een samenvatting van de schooldag. |

Alle blueprints:

- werken per kind of per account (je kiest de juiste sensor);
- melden **alleen nieuwe dingen** – bestaande items geven geen tweede melding;
- sturen **geen** meldingen na een herstart van Home Assistant (geen push-spam);
- kunnen optioneel een `input_boolean` als hoofdschakelaar en/of per-type
  schakelaar gebruiken.

## Vereisten

- De integratie **`magister_school`** met de overzichtsensor per kind
  (`sensor.magister_<naam>`).
- Voor `magister_berichten.yaml`: integratie **v2.4.0** of nieuwer (de sensoren
  `sensor.magister_data_ongelezen_berichten` en
  `sensor.magister_data_mededelingen`).
- **Home Assistant 2024.8** of nieuwer (notify-entiteiten + `notify.send_message`).
- De **Home Assistant Companion-app** op je telefoon (die levert de
  `notify.<toestel>`-entiteit).

---

## Installatie

### Manier 1 – met de import-knop (makkelijkst)

[![Open je Home Assistant en toon het blueprint-importvenster.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_melding.yaml)

[![Open je Home Assistant en toon het blueprint-importvenster.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_berichten.yaml)

[![Open je Home Assistant en toon het blueprint-importvenster.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2FOdynBrouwer%2Fmagister-school-integration%2Fmain%2Fblueprints%2Fautomation%2Fmagister_school%2Fmagister_dagoverzicht.yaml)

### Manier 2 – bestand kopiëren

1. Kopieer de map `blueprints/automation/magister_school/` naar
   `config/blueprints/automation/` in je Home Assistant-configuratie.
2. Herstart Home Assistant (of ververs de pagina als de blueprints al zichtbaar zijn).
3. Ga naar **Instellingen → Automatiseringen → Blueprints**.

---

## Automations aanmaken

Ga naar **Instellingen → Automatiseringen → Blueprints**, kies de blueprint en
klik op **Automation maken**.

Maak voor de eerste blueprint **vijf** automations, met deze instellingen:

| Soort melding | Aangeraden schakelaar (optioneel) | Titel van de push |
|---|---|---|
| Lesuitval | `input_boolean.magister_lesuitval` | Magister - lesuitval |
| Nieuw huiswerk | `input_boolean.magister_huiswerk` | Magister - nieuw huiswerk |
| Nieuwe cijfers | `input_boolean.magister_cijfers` | Magister - nieuw cijfer |
| Nieuwe absentie | `input_boolean.magister_absenties` | Magister - absentie |
| Roosterwijziging | `input_boolean.magister_roosterwijzigingen` | Magister - roosterwijziging |

Voor de tweede blueprint maak je **twee** automations:

| Soort melding | Sensor | Aangeraden schakelaar (optioneel) | Titel van de push |
|---|---|---|---|
| Nieuwe berichten | `sensor.magister_data_ongelezen_berichten` | `input_boolean.magister_berichten` | Magister - nieuw bericht |
| Nieuwe mededelingen | `sensor.magister_data_mededelingen` | `input_boolean.magister_mededelingen` | Magister - nieuwe mededeling |

Heb je meerdere kinderen? Maak dan per kind dezelfde set automations en kies
telkens de juiste sensor. De berichten- en mededelingen-sensoren zijn
**accountbreed**, dus daar is één set genoeg.

Voor het dagoverzicht maak je één automation met de derde blueprint.

### Velden

| Veld | Verplicht | Betekenis |
|---|---|---|
| Magister-sensor | **ja** | De overzichtsensor van het kind, of de berichten-/mededelingen-sensor. |
| Notificatie-doel | ja, om meldingen te krijgen | De `notify.<toestel>`-entiteit. Leeg laten mag, maar dan komt er niets. |
| Soort melding | ja | Welk type melding deze automation verstuurt. |
| Hoofdschakelaar | nee | Alleen melden als deze helper aan staat. Leeg = altijd melden. |
| Schakelaar voor dit type | nee | Idem, per meldingstype. Leeg = altijd melden. |

---

## Optionele schakelaars (helpers)

Een **blueprint kan geen helpers aanmaken** – Home Assistant heeft daar geen
service voor. Je hebt twee mogelijkheden:

1. **Geen helpers gebruiken** (standaard): laat de schakelaarvelden leeg en zet
   de automation zelf aan of uit.
2. **Wel helpers gebruiken:** zet [`packages/magister_helpers.yaml`](packages/magister_helpers.yaml)
   in `config/packages/` en herstart Home Assistant. De 9 schakelaars bestaan dan
   meteen. Of maak ze met de hand: **Instellingen → Apparaten & diensten →
   Helpers → Boolean**.

> Definieer de helpers maar op één plek. Heb je ze al in een ander package of in
> de UI staan, voeg dit bestand dan niet toe.

---

## Zo werken de meldingen

De integratie haalt de Magister-gegevens elke 15 minuten op (instelbaar in de
integratie-opties). Een melding komt dus binnen **maximaal ~15 minuten** nadat
Magister de wijziging registreert.

| Melding | Wanneer |
|---|---|
| Lesuitval | de les zelf is vervallen (`status` bevat "Vervallen" en het item is een les) |
| Nieuw huiswerk | een nieuw huiswerkitem dat nog niet afgerond is |
| Nieuwe cijfers | een nieuw cijfer in de voortgangscijfers |
| Nieuwe absentie | een nieuwe absentiemelding |
| Roosterwijziging | een les die gewijzigd is in tijd, lokaal, docent of vak |
| Nieuw bericht / mededeling | een item dat nog niet in de vorige stand van `laatste` stond (vergeleken op onderwerp + datum + afzender) |
| Dagelijks overzicht | op de gekozen dagen op het gekozen tijdstip |

**Geen dubbele meldingen:** items worden vergeleken met de vorige stand
(identiteit per type, bijv. cijfer = vak + kolom + periode). Een bestaand item
dat wordt aangepast levert geen nieuwe melding op. Bij berichten geldt: het
attribuut `laatste` bevat de vijf nieuwste items, dus komen er meer dan vijf
tussen twee verversingen binnen, dan meldt de automation alleen de vijf die de
sensor toont.

---

## FAQ

**Krijg ik een melding als een les wordt vervangen (andere docent of lokaal)?**
Nee, dat is geen lesuitval. Je krijgt dan een melding **Roosterwijziging**.

**Waarom krijg ik na een herstart geen melding van iets dat al vervallen was?**
Dat is bewust: de eerste meting na een herstart wordt overgeslagen om te
voorkomen dat je alle bestaande items als "nieuw" binnenkrijgt.

**Krijg ik een melding als ik een bericht lees?**
Nee. Lezen verandert alleen de telling; de melding gaat over een bericht dat er
nog niet was. Onderwerp, datum en afzender samen bepalen of iets nieuw is.

**Mijn mededelingen-sensor blijft op 0 staan.**
Dan publiceert jouw school geen mededelingen. De sensor werkt wel; er is alleen
niets te melden.

**Kan ik sneller meldingen krijgen?**
Ja: zet in de integratie-opties het poll-interval lager (minimaal 60 seconden).
Let op: dat betekent meer verzoeken naar Magister.

**Kan de blueprint de helpers voor me aanmaken?**
Nee. Gebruik het optionele package of laat de schakelaars leeg.

**Ik heb twee kinderen.**
Maak per kind dezelfde set automations en kies de juiste sensor.

---

## Bestandsstructuur

```
blueprints/automation/magister_school/
├── magister_melding.yaml
├── magister_berichten.yaml
└── magister_dagoverzicht.yaml
packages/
└── magister_helpers.yaml        (optioneel)
```

## Changelog

**1.1.0**
- Nieuwe blueprint `magister_berichten.yaml`: melding bij een nieuw bericht of
  een nieuwe mededeling, met onderwerp en afzender.
- Twee extra helpers in het optionele package (`magister_berichten`,
  `magister_mededelingen`).
- Alle bestaande invoervelden gecontroleerd tegen de werkelijke
  sensor-attributen en item-velden van de integratie; geen wijzigingen nodig.

**1.0.0**
- Eerste versie: 5 gebeurtenis-meldingen + dagelijks overzicht.
- Optionele hoofdschakelaar en per-type schakelaars.
- Dedupe op identiteit per meldingstype; geen meldingen na een herstart.

## Licentie

Vrij te gebruiken en aan te passen. Naamsvermelding niet verplicht, wel netjes.

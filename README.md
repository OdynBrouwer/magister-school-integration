[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/OdynBrouwer/magister-school-integration.svg)](https://github.com/OdynBrouwer/magister-school-integration/releases)
[![License](https://img.shields.io/github/license/OdynBrouwer/magister-school-integration.svg)](LICENSE)

Integreer Magister schoolinformatie direct in je Home Assistant dashboard. Toon roosters, cijfers, huiswerk en meer voor al je kinderen in één overzicht.

## 🚀 Features

- **📅 Rooster & Afspraken** - Toon het dagelijkse rooster en afspraken
- **📊 Cijfers Overzicht** - Houd alle cijfers en resultaten bij
- **📚 Huiswerk & Opdrachten** - Toon openstaande huiswerkopdrachten
- **⚠️ Roosterwijzigingen** - Blijf op de hoogte van laatste wijzigingen
- **👨‍👩‍👧‍👦 Multi-Kind Support** - Ondersteuning voor meerdere kinderen
- **👤 Student Accounts** - Studenten kunnen hun eigen account gebruiken
- **🔄 Automatische Updates** - Data wordt regelmatig ververst
- **🎨 Ingebouwde Lovelace Card** - Mooie dashboardweergave, automatisch meegeleverd en als dashboard-resource geregistreerd
- **🔗 Unieke ID's per account** – Meerdere accounts naast elkaar zonder dubbele entities
- **🔐 Multi-Account Support** - Gebruik meerdere accounts tegelijk zonder conflicts
- **📖 Studiewijzers** - Volledige studiewijzer-teksten met behoud van lijstopmaak
- **🚫 Uitval & Wijzigingen** - Vervallen lessen verschijnen ook in de roosterwijzigingen
- **💾 Recorder-vriendelijk** - Omvangrijke attributen automatisch uitgesloten van de recorder-historie

## ✨ Nieuw in v2.3.x

- **Dashboard-card ingebouwd** — de Magister School Card wordt nu meegeleverd in `custom_components/magister_school/www/` en bij het opstarten automatisch als dashboard-resource geregistreerd. Geen aparte HACS-plugin meer nodig; integratie en card blijven altijd in versie gelijk.
- **Unique IDs per config entry** — alle entities krijgen een ID die aan het config entry is gekoppeld, zodat meerdere accounts (en twee ouders met hetzelfde kind) geen `_1`-suffixen meer veroorzaken.
- **Automatische migratie** — bestaande installaties behouden hun entity-ID's; de unique IDs worden eenmalig omgezet.
- **`poll_interval` werkt nu echt** — de optie werd opgeslagen maar genegeerd; de coordinator gebruikt hem nu voor het update-interval (standaard 900 s = 15 minuten, bereik 60-86400).
- **Inlogfouten herkend** — het script geeft een eigen exitcode bij een mislukte login, waardoor Home Assistant nu netjes een re-authenticatie start in plaats van de integratie stil `unavailable` te laten worden.
- **Correcte tijdzone** — `ZoneInfo` wordt nog maar één keer op moduleniveau aangemaakt in plaats van in de event loop.
- **Nettere entity-registry** — de oude, niet aan de integratie gebonden suffix-cleanup is verwijderd.

## ✨ Nieuw in v2.2.x

- **Studiewijzers met volledige tekst** (`studiewijzers`) — volledige sectietekst i.p.v. previews, met behoud van lijstopmaak
- **Uitval in wijzigingen** — vervallen lessen uit de afspraken worden nu ook aan de roosterwijzigingen toegevoegd (`is_uitval`)
- **Correcte kindnamen met Tussenvoegsel** (bv. "Jan van Tilburg" i.p.v. "Jan Tilburg")
- **Recorder-vriendelijk (#39)** — omvangrijke attributen worden via `_unrecorded_attributes` automatisch uitgesloten van de recorder-historie; geen 16 KB-waarschuwingen meer, zonder handmatige `recorder.exclude`
- Eerder in v2.1.0: **klas & profiel**, **voortgangscijfers**, **absenties** en **les-extra's** in afspraken

## 📋 Vereisten

- Home Assistant 2023.8.0 of hoger
- Magister account met toegang (ouder of student account)
- HACS (aanbevolen) of handmatige installatie

## 🔧 Installatie

### Via HACS (Aanbevolen)

[![Open deze repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=OdynBrouwer&repository=magister-school-integration&category=integration)

### Handmatige Installatie

1. Kopieer de `custom_components/magister_school` map naar je `custom_components` directory
2. Herstart Home Assistant

## ⚙️ Configuratie

1. Ga naar **Settings** → **Devices & Services**
2. Klik op **+ Add Integration**
3. Zoek naar **"Magister School"**
4. Voer je inloggegevens in:
   - **School**: Je schoolnaam (bijv. `zuidermavo`, zónder `.magister.net`)
   - **Gebruikersnaam**: Je Magister gebruikersnaam
   - **Wachtwoord**: Je Magister wachtwoord
   - **2FA/TOTP-secret** (optioneel): alleen nodig bij 2FA. Vul hier de **secret key** in (de lange base32-string uit je authenticator-app, bijv. via ProtonPass of Aegis), **niet** de 6-cijferige code zelf.

### 👤 Student vs Ouder Accounts

De integratie werkt met beide account types:

- **Ouder Account**: Toont data voor alle gekoppelde kinderen
- **Student Account**: Toont data voor de ingelogde student zelf

Je kunt ook meerdere accounts tegelijk configureren zonder conflicts!

### ⚙️ Opties

Ga naar **Settings** → **Devices & Services** → **Magister** → **Configure**:

| Optie | Standaard | Bereik | Betekenis |
|---|---|---|---|
| `poll_interval` | 900 | 60-86400 | Update-interval in seconden (900 = 15 minuten) |
| `dagen_terug` | 0 | 0+ | Hoeveel dagen terug ophalen (0 = vandaag) |
| `dagen_vooruit` | 14 | 0+ | Hoeveel dagen vooruit ophalen (14 = twee weken) |

Wijzigingen worden direct toegepast: de integratie herlaadt zichzelf.

## 📊 Beschikbare Sensors

Na installatie worden de volgende sensors aangemaakt:

### Hoofd Sensor
- `sensor.magister_data` - Laatste update-tijdstip van de integratie

### Per Kind Sensors
- `sensor.magister_[kind_naam]` - Compleet overzicht
- `sensor.magister_[kind_naam]_afspraken_vandaag` - Aantal afspraken vandaag
- `sensor.magister_[kind_naam]_huiswerk` - Aantal huiswerk items
- `sensor.magister_[kind_naam]_volgende_afspraak` - Volgende afspraak
- `sensor.magister_[kind_naam]_cijfers` - Cijfers overzicht
- `sensor.magister_[kind_naam]_afspraken` - Alle afspraken
- `sensor.magister_[kind_naam]_wijzigingen` - Roosterwijzigingen
- `sensor.magister_[kind_naam]_opdrachten` - Opdrachten
- `sensor.magister_[kind_naam]_absenties` - Absenties
- `sensor.magister_[kind_naam]_studiewijzers` - Studiewijzers
- `sensor.magister_[kind_naam]_activiteiten` - Activiteiten
- `sensor.magister_[kind_naam]_aanmeldingen` - Aanmeldingen

### 🔗 Unieke ID's per account

Elke entity krijgt een unique ID die begint met het ID van het config entry
(bijvoorbeeld `<entry_id>_magister_jan_huiswerk`). Daardoor kunnen meerdere
accounts naast elkaar bestaan zonder dat Home Assistant `_1`, `_2`-suffixen
toevoegt aan de entity-ID's.

Bij het opstarten worden bestaande unique IDs eenmalig omgezet naar het nieuwe
formaat. De **entity-ID's blijven daarbij ongewijzigd**, dus je dashboards,
templates en automations blijven werken.

## 📊 Attributen & voorbeelden

Elk kind krijgt een **overzicht-sensor** `sensor.magister_[kind_naam]`
(bijv. `sensor.magister_Odyn_brouwer`). Alle data staat hierin als
**attributen**, zodat je alles in templates en automations kunt gebruiken.

### Basisinfo

| Attribuut | Voorbeeld | Beschrijving |
|---|---|---|
| `naam` | `Odyn Brouwer` | Volledige naam |
| `stamnummer` | `12552` | Magister stamnummer |
| `geboortedatum` | `2010-07-20` | Geboortedatum |
| `klas` | `Gymnasium 3b` | Huidige klas (uit actieve aanmelding) |
| `profiel` | `NT` | Profiel (alleen bovenbouw) |

### Tellingen

| Attribuut | Beschrijving |
|---|---|
| `aantal_afspraken_vandaag` | Aantal afspraken vandaag |
| `aantal_huiswerk` / `aantal_huiswerk_onafgerond` | Open (niet afgerond) huiswerk |
| `aantal_huiswerk_totaal` | Totaal huiswerk (open + afgerond) |
| `aantal_huiswerk_afgerond` | Afgerond huiswerk |
| `aantal_uitval` | Vervallen lessen |

### Schooltijden

| Attribuut | Voorbeeld |
|---|---|
| `school_start_vandaag` | `08:35` |
| `school_einde_vandaag` | `15:15` |
| `volgende_schooldag` | `2026-09-14` |
| `volgende_schooldag_start` | `08:35` |
| `volgende_schooldag_einde` | `14:25` |
| `volgende_afspraak` | `2026-09-14 08:35:00` |
| `volgende_vak` | `Natuurkunde` |
| `lessen_vandaag` | Lijst met lessen van vandaag |

### Afspraken & roosterwijzigingen

`afspraken` en `wijzigingen` zijn lijsten. Elk item bevat:

| Veld | Voorbeeld | Beschrijving |
|---|---|---|
| `start` / `einde` | `2026-09-14 08:35:00` | Begin- en eindtijd |
| `status` | `Les` | Status-tekst |
| `soort` | `Les` / `Algemeen` | Soort afspraak |
| `omschrijving` | `wisb - wld - g5.wisb1` | Vak - docent - groep |
| `opmerking` | `Neem boek mee` | Extra opmerking |
| `inhoud` | `Maak opgave 25...` | Huiswerk-inhoud (zonder HTML) |
| `is_online` | `true` / `false` | Online les |
| `duurt_hele_dag` | `true` / `false` | Duurt de hele dag |
| `lokaal` | `440` | Lokaal |
| `vak` | `Wiskunde B` | Vaknaam |
| `vak_id` | `12111` | Vak-Id |
| `docent` | `Willems` | Docentnaam |
| `docentcode` | `WLD` | Docentcode |
| `is_huiswerk` | `true` / `false` | Heeft huiswerk |
| `is_afgerond` | `true` / `false` | Huiswerk afgerond |
| `is_uitval` | `true` / `false` | Les vervallen |
| `was_afwijkend` | `true` / `false` | Les gewijzigd |
| `lesuurstart` / `lesuureinde` | `1` | Lesuren |

### Cijfers

`cijfers` (recente cijfers):

| Veld | Voorbeeld |
|---|---|
| `vak` | `ne` |
| `omschrijving` | `Nulmeting werkwoordspelling` |
| `waarde` | `6,0` |
| `weegfactor` | `0` |
| `ingevoerd_op` | `2026-09-02 14:54:14` |

`voortgangscijfers` (volledige cijfers van het huidige schooljaar):

| Veld | Voorbeeld |
|---|---|
| `lesperiode` | `2627` |
| `vak` | `ne` |
| `vak_id` | `14478` |
| `kolom` | `ne101` |
| `omschrijving` | `so/pw` |
| `periode` | `per1` |
| `waarde` | `6,0` |
| `cijfer` | `6` |
| `weegfactor` | `1` |
| `is_voldoende` | `true` / `false` |
| `telt_mee` | `true` / `false` |
| `moet_inhalen` | `true` / `false` |
| `vrijstelling` | `true` / `false` |
| `ingevoerd_op` | `2026-09-02 14:54:14` |

### Absenties

| Veld | Voorbeeld | Beschrijving |
|---|---|---|
| `start` | `2025-09-18 00:00:00` | Datum |
| `omschrijving` | `Ongeoorloofd afwezig` | Reden |
| `afspraak` | `ml - brt - g2c` | Gekoppelde les |
| `geoorloofd` | `true` / `false` | Geoorloofd? |
| `code` | `oa` / `BV` / `HV` / `tl` | Absentie-code |
| `lesuur` | `1` | Lesuur |

### Template voorbeelden

```jinja2
Klas: {{ state_attr('sensor.magister_Odyn_brouwer', 'klas') }}
Profiel: {{ state_attr('sensor.magister_Odyn_brouwer', 'profiel') }}
Open huiswerk: {{ state_attr('sensor.magister_Odyn_brouwer', 'aantal_huiswerk') }}

{# Nieuwste cijfer dit schooljaar #}
{% set v = state_attr('sensor.magister_Odyn_brouwer', 'voortgangscijfers')
           | selectattr('ingevoerd_op')
           | sort(attribute='ingevoerd_op', reverse=true) | list %}
{% if v %}
  Laatste cijfer: {{ v[0].vak|upper }} {{ v[0].waarde }} ({{ v[0].omschrijving }})
{% endif %}

{# Aantal ongeoorloofde absenties #}
{{ state_attr('sensor.magister_Odyn_brouwer', 'absenties')
   | selectattr('geoorloofd', 'eq', false) | list | count }}
```

### Voorbeeld template sensor

```yaml
template:
  - sensor:
      - name: "Odyn gemiddelde dit jaar"
        state: >
          {% set c = state_attr('sensor.magister_Odyn_brouwer', 'voortgangscijfers')
                     | selectattr('telt_mee', 'eq', true)
                     | selectattr('cijfer') | list %}
          {% if c %}
            {{ ((c | map(attribute='cijfer') | map('float') | sum) / (c | length)) | round(1) }}
          {% else %}
            0
          {% endif %}
```

### Automations

```yaml
# Notificatie bij een nieuw cijfer
automation:
  - alias: "Nieuw cijfer"
    trigger:
      - platform: state
        entity_id: sensor.magister_Odyn_brouwer
    condition:
      - condition: template
        value_template: >
          {{ (state_attr('sensor.magister_Odyn_brouwer', 'voortgangscijfers') | length) >
             (trigger.from_state.attributes.get('voortgangscijfers', []) | length) }}
    action:
      - service: notify.mobile_app
        data:
          message: "Er is een nieuw cijfer!"

# Herinnering voor huiswerk
automation:
  - alias: "Huiswerk herinnering"
    trigger:
      platform: time
      at: "18:00:00"
    condition:
      condition: template
      value_template: "{{ states('sensor.magister_Odyn_brouwer_huiswerk') | int > 0 }}"
    action:
      service: notify.mobile_app
      data:
        message: "Nog {{ states('sensor.magister_Odyn_brouwer_huiswerk') }} huiswerk items open!"
```

## 🎨 Lovelace Card

De **Magister School Card** zit sinds **v2.3.0** in deze integratie. Na het
herstarten van Home Assistant staat de resource automatisch in je dashboard en
kun je de kaart direct gebruiken — je hoeft dus geen aparte HACS-plugin te
installeren.

```yaml
type: custom:magister-school-card
entity: sensor.magister_naam_kind
```

De kaart wordt geserveerd vanaf `/magister_school/magister-school-card.js` en
automatisch als dashboard-resource toegevoegd. Werkt de kaart niet meteen?
Doe een harde refresh (Ctrl+F5) in de browser.

> De losse repository [magister-school-card](https://github.com/OdynBrouwer/magister-school-card)
> blijft bestaan voor ontwikkeling, maar de versie in deze integratie is leidend.
## 🐛 Problemen Oplossen

### Geen data zichtbaar
- Controleer je inloggegevens
- Check de Home Assistant logs voor foutmeldingen
- Zorg dat je Magister account actief is

### Sensors niet verschijnen
- Herstart Home Assistant
- Controleer of de integration correct geïnstalleerd is
- Kijk in Developer Tools → States voor beschikbare sensors

### Verbindingsproblemen
- Controleer je internetverbinding
- Zorg dat je school Magister ondersteunt
- Probeer opnieuw te authenticeren

## 📝 Logs Bekijken

Ga naar **Developer Tools** → **Logs** en zoek naar `magister` voor gedetailleerde logging.

## 🤝 Bijdragen

Bijdragen zijn welkom! Voel je vrij om:
- Issues te openen voor bugs of feature requests
- Pull requests in te dienen voor verbeteringen
- De documentatie te verbeteren

## 🛠️ Ontwikkeling & HACS-standaarden

De repository volgt de HACS- en Home Assistant-validatieprocessen:

- **GitHub Actions** voert bij elke push en pull request automatisch de
  HACS- en hassfest-validatie uit (`.github/workflows/validate.yml`).
- **pre-commit** bevat handige lokale checks. Installeer dit optioneel met:
  `pip install pre-commit && pre-commit install`
- **Ruff** is ingesteld met een gematigde, veilige regelselectie (zie
  `.ruff.toml`) om bestaande code niet onnodig te herschrijven.

Voor indiening in de **HACS-defaultstore** is nog nodig:
- Een goedgekeurde aanvraag in [hacs/default](https://github.com/hacs/default/pulls)
- Een brand-entry in [home-assistant/brands](https://github.com/home-assistant/brands)
  voor het logo vóór installatie (het icoon in `brand/icon.png` wordt gebruikt
  zodra de integratie geïnstalleerd is)

## 🗃️ Database

Omvangrijke attributen worden sinds **v2.2.1** automatisch uitgesloten van de
recorder-historie via `_unrecorded_attributes`. De data blijft live beschikbaar
voor de card en templates; alleen de historie in de database wordt overgeslagen.
Geen handmatige `recorder.exclude` meer nodig.


## 📄 Licentie

Deze integratie is vrijgegeven onder de MIT licentie. Zie het [LICENSE](LICENSE) bestand voor details.

### Credits

`custom_components/magister_school/script/magister.py` is deels gebaseerd op
[nlitsme/magister-tool](https://github.com/nlitsme/magister-tool) van
Willem Hengeveld, eveneens MIT-gelicenseerd. De bijbehorende copyright- en
licentietekst staat boven aan dat bestand.

## ⚠️ Disclaimer

Deze integratie is niet officieel geassocieerd met Magister. Gebruik op eigen risico. Zorg dat je voldoet aan de gebruiksvoorwaarden van Magister.

## 🔗 Links

- [GitHub Repository](https://github.com/OdynBrouwer/magister-school-integration)
- [Lovelace Card](https://github.com/OdynBrouwer/magister-school-card)
- [Issue Tracker](https://github.com/OdynBrouwer/magister-school-integration/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant community**




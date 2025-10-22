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
- **🔄 Automatische Updates** - Data wordt regelmatig ververst
- **🎨 Lovelace Card** - Mooie weergave voor je dashboard ([separate card available](https://github.com/OdynBrouwer/magister-school-card))

## 📋 Vereisten

- Home Assistant 2023.8.0 of hoger
- Magister account met toegang tot de API
- HACS (aanbevolen) of handmatige installatie

## 🔧 Installatie

### Via HACS (Aanbevolen)

1. Ga naar **HACS** → **Integrations**
2. Klik op **+** (Custom repositories)
3. Voeg toe: `https://github.com/OdynBrouwer/magister-school-integration`
4. Selecteer categorie: **Integration**
5. Klik **Install**
6. Herstart Home Assistant

### Handmatige Installatie

1. Kopieer de `custom_components/magister_school` map naar je `custom_components` directory
2. Herstart Home Assistant

## ⚙️ Configuratie

1. Ga naar **Settings** → **Devices & Services**
2. Klik op **+ Add Integration**
3. Zoek naar **"Magister School"**
4. Voer je inloggegevens in:
   - **School**: Je schoolnaam (bijv. `zuidermavo`)
   - **Gebruikersnaam**: Je Magister gebruikersnaam
   - **Wachtwoord**: Je Magister wachtwoord

## 📊 Beschikbare Sensors

Na installatie worden de volgende sensors aangemaakt:

### Hoofd Sensor
- `sensor.magister_main_data` - Overzicht van alle data

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

### 🧹 Automatische cleanup van duplicaat-entities (suffixes zoals `_1`, `_2`)

Na een update via HACS kan het soms voorkomen dat Home Assistant tijdelijk entities opnieuw registreert, wat leidt tot suffixes zoals `_1`, `_2`, etc. in entity-namen (bijv. `sensor.magister_jan_huiswerk_1`).

Vanaf versie **1.x.x** (of: *in de volgende release*) voert de integratie **automatisch een cleanup uit bij opstart**:
- Entities met suffixes (`_1` t/m `_5`) worden hernoemd naar de originele naam **als die nog niet bestaat**.
- Dit gebeurt **één keer per opstart**, zonder prestatieverlies.
- Als er suffixes zijn opgeruimd, verschijnt er een melding in Home Assistant.

> 💡 **Handmatig opruimen?**  
> Verwijder oude entities handmatig via **Settings → Devices & Services → Entities**, of herstart Home Assistant om de automatische cleanup te activeren.

Deze functionaliteit maakt gebruik van de **entity registry** en is volledig veilig.

## 🎨 Lovelace Card

Voor een mooie dashboard weergave, installeer de [Magister School Lovelace Card](https://github.com/OdynBrouwer/magister-school-card):

```yaml
type: custom:magister-school-card
entity: sensor.magister_naam_kind


# Notificatie bij nieuwe cijfers
automation:
  - alias: "Notificatie bij nieuwe cijfers"
    trigger:
      platform: state
      entity_id: sensor.magister_jan_cijfers
    action:
      service: notify.mobile_app
      data:
        message: "Er is een nieuw cijfer toegevoegd!"
        
# Herinnering voor huiswerk
automation:
  - alias: "Huiswerk herinnering"
    trigger:
      platform: time
      at: "18:00:00"
    condition:
      condition: template
      value_template: "{{ states('sensor.magister_jan_huiswerk') | int > 0 }}"
    action:
      service: notify.mobile_app
      data:
        message: "Nog {{ states('sensor.magister_jan_huiswerk') }} huiswerk items open!"
```
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

## 📄 Licentie

Deze integratie is vrijgegeven onder de MIT licentie. Zie het [LICENSE](LICENSE) bestand voor details.

## ⚠️ Disclaimer

Deze integratie is niet officieel geassocieerd met Magister. Gebruik op eigen risico. Zorg dat je voldoet aan de gebruiksvoorwaarden van Magister.

## 🔗 Links

- [GitHub Repository](https://github.com/OdynBrouwer/magister-school-integration)
- [Lovelace Card](https://github.com/OdynBrouwer/magister-school-card)
- [Issue Tracker](https://github.com/OdynBrouwer/magister-school-integration/issues)
- [Home Assistant Community](https://community.home-assistant.io/)

---

**Made with ❤️ for the Home Assistant community**




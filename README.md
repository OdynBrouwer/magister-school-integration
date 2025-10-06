# Magister School Integration for Home Assistant

Integreer Magister schoolinformatie in Home Assistant.

## Features
- Rooster en afspraken
- Cijfers overzicht
- Huiswerk opdrachten
- Roosterwijzigingen
- Absenties
- En meer!

## Installation

### Via HACS (aanbevolen)
1. Voeg deze repository toe als custom repository in HACS
2. Zoek naar "Magister School" en installeer
3. Herstart Home Assistant

### Handmatig
1. Kopieer de `custom_components/magister_school` map naar je `custom_components` directory
2. Voeg de card toe aan je `www` map en resources
3. Herstart Home Assistant

## Configuration
Voeg via Settings → Devices & Services → Add Integration → Zoek "Magister School"

## Lovelace Card
```yaml
type: custom:magister-school-card
entity: sensor.magister_kind_naam# magister-school-integration

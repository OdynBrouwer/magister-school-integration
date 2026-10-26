# Release v2.3.1

## GitHub release text

Magister School Integration v2.3.1 maakt het onderscheid tussen echte lessen, echte afspraken en lokaal-/groepsreserveringen, splitst de schooltijden in een start- en eindtijd met eigen regels, en neemt twee bijdragen van @Niek mee: timeout-herstel en weerbaarheid tegen incomplete Magister-data.

### Nieuw: `categorie` op elke afspraak

Magister gebruikt `soort: Algemeen` voor drie verschillende dingen. De integratie classificeert ze nu:

| `categorie` | Wat het is | Voorbeeld | Vak/docent |
|---|---|---|---|
| `les` | een echt lesuur | `wisb - wld - g5.wisb1` | ja |
| `afspraak` | een echte afspraak | nulmeting, mentorgesprek | minstens één |
| `boeking` | lokaal-/groepsreservering | `Studie na school`, `10 leerlingen` | nee |

Die laatste groep is geen afspraak voor je kind maar een gereserveerd lokaal, bijvoorbeeld voor een studie-uur of een avondactiviteit. Filter erop in templates, of gebruik de nieuwe kaartoptie.

### Nieuw: kaartoptie `hide_boekingen`

Verbergt de `boeking`-items in de roosterwidgets. Standaard **uit**: zonder de optie blijven ze zichtbaar met een 📌 **Boeking**-badge en gedempte stijl, zodat je het verschil ziet zonder iets kwijt te raken.

```yaml
type: custom:magister-school-card
entity: sensor.magister_voornaam_achternaam
layout: auto
hide_layout_selector: true
hide_kind_info: false
hide_boekingen: false        # true = Studie na school en avondblokken verbergen
show_widgets:
  - stats
  - week_schooltijden
  - rooster_meta
  - rooster_morgen
  - volgende_les
  - huiswerk
  - cijfers
  - voortgangscijfers
  - opdrachten
  - wijzigingen
  - schooltijden
  - volgende_schooldag
```

### Hoe de schooltijden nu werken

Start en eind volgen bewust **niet** dezelfde regel:

| | Wat telt mee | Waarom |
|---|---|---|
| **`school_start_vandaag`** | lessen **en** afspraken met een vak of docent | een nulmeting om 08:00 betekent dat je kind er om 08:00 moet zijn, ook als de eerste les om 08:35 begint |
| **`school_einde_vandaag`** | alleen echte lessen | een optioneel studie-uur of avondactiviteit betekent niet dat je kind tot 20:40 op school zit |

Een niet-lesitem telt alleen mee als het een **vak of docent** heeft, binnen **05:00-18:00** valt, **niet** elke werkdag terugkeert en geen bloktype is. Vervallen items en hele-dag-items tellen nooit mee.

Praktisch: gebruik `school_start_vandaag` voor je wekker en `school_einde_vandaag` voor "wanneer kan ik mijn kind ophalen?".

### Nieuw: kaartbron in deze repository

De kaart wordt nu gebouwd uit `card/` naar `custom_components/magister_school/www/`. Bron en bundel kunnen daardoor niet meer uiteenlopen. Bouwen: `cd card && npm install && npm run build`.

### Opgelost

- **Schooltijden negeerden geplande activiteiten (#43)** - de sensoren filterden op soort `Les`, waardoor een nulmeting (`Algemeen`) genegeerd werd en de wekker te laat stond.
- **Ongeldige schoolnaam gaf een misleidende fout (#45)** - een weergavenaam met spaties of `&` kan nooit een tenant-slug zijn. Het formulier meldt nu `invalid_school` met uitleg, en `Trevianum`, `trevianum.magister.net` en volledige URL's worden genormaliseerd naar `trevianum`.
- **`herhalend` en `herhalend_elke_werkdag` ontbraken** - Magister's `Herhaling`/`HerhaalStatus` werden niet doorgegeven. Beide afsprakenlijsten gaan nu door dezelfde mapper, zodat velden niet meer kunnen uiteenlopen.
- **Dubbele lokaalnaam** - `lokaal` gaf "440, 440"; nu "440".

### Bijdragen van @Niek

- **Timeout-herstel (#42)** - een mislukte fetch zette de integratie stil. Nu: 15 s HTTP-timeout, 90 s per fetch, een retry na 2 s bij een timeout. Bij aanhoudend falen verschijnt een **Settings -> Repairs**-melding per account die vanzelf verdwijnt zodra er weer data is. Verlopen tokens worden niet meer geaccepteerd.
- **Weerbaar tegen incomplete data (#44)** - een studiewijzer zonder `Onderdelen` liet de hele refresh crashen met `KeyError`. Alle optionele collecties worden nu met gedeelde guards uitgelezen: geldige records blijven, ontbrekende secties komen in `data_warnings` en in de log. Een 401 of verlopen `SecurityToken` breekt de fetch nog steeds af.

### Met dank aan

- @barrymossel (#43)
- @cautje (#45)
- @Niek (#42, #44)

## HACS update text

Afspraken krijgen een `categorie` (les / afspraak / boeking) met een kaartoptie `hide_boekingen`, en de schooltijden hebben nu een eigen regel voor start en eind: een nulmeting telt mee voor de start, een optioneel studie-uur duwt de eindtijd niet op.

## Previous release: v2.3.0

# Release v2.3.0

## GitHub release text

Magister School Integration v2.3.0 levert de dashboard-card mee, geeft elke entity een unieke ID per account en verwerkt de reviewpunten van de HACS-defaultstore ([hacs/default#10760](https://github.com/hacs/default/pull/10760)).


### ⚠️ Migratie: oude losse card verwijderen

De card zit nu in de integratie. Heb je de losse **Magister School Card** via
HACS geïnstalleerd? Verwijder die na de update, anders worden er twee kopieën
van dezelfde kaart geladen:

1. Werk de integratie bij en herstart Home Assistant (de kaart doet het daarna al).
2. Ga naar **HACS → Frontend → Magister School Card → menu → Remove**.
3. Controleer bij **Instellingen → Dashboards → Resources** of er geen
   `/hacsfiles/magister-school-card/...` meer tussen staat.
4. Herstart Home Assistant en doe een harde refresh (Ctrl+F5).

Je dashboards blijven werken: de kaartnaam `custom:magister-school-card` is
hetzelfde.

### Nieuw

- **Ingebouwde dashboard-card**: de Magister School Card wordt meegeleverd in `custom_components/magister_school/www/`, geserveerd op `/magister_school/magister-school-card.js` en bij het opstarten automatisch als dashboard-resource geregistreerd. Integratie en card blijven zo altijd in versie gelijk; de losse card-plugin is niet meer nodig.
- **`poll_interval` werkt nu echt**: de optie werd opgeslagen maar genegeerd. De coordinator gebruikt hem nu voor het update-interval (standaard 900 s, bereik 60-86400).

### Opgelost

- **Unique IDs per config entry**: alle sensoren en kalenders krijgen een unique ID die aan het config entry is gekoppeld. Meerdere accounts, of twee ouders met hetzelfde kind, geven geen `_1`-suffixen meer. Bestaande installaties worden eenmalig gemigreerd met behoud van hun entity-ID's.
- **Re-authenticatie bij inlogfouten**: het script geeft nu een eigen exitcode (`2`) plus marker bij een mislukte login, zodat `AuthenticationRequired` echt wordt opgegooid. Een verlopen wachtwoord start nu netjes de reauth-flow in plaats van de integratie stil `unavailable` te maken.
- **Timezone buiten de event loop**: `ZoneInfo("Europe/Amsterdam")` wordt één keer op moduleniveau aangemaakt in plaats van in de `event`-property en `async_get_events`.
- **Entity-registry opgeschoond**: de suffix-cleanup die over de volledige entity registry liep is verwijderd; de unique-ID-fix maakt hem overbodig.
- **Card**: hardcoded naam-mapping verwijderd, zodat de kaart voor iedereen de juiste naam toont.

### Met dank aan

- @frenck voor de grondige review van de HACS-aanvraag
- @Niek (#39)

## HACS update text

Dashboard-card wordt nu meegeleverd en automatisch geregistreerd, unique IDs zijn per account gescheiden, `poll_interval` werkt en inlogfouten starten een re-authenticatie.

## Previous release: v2.2.1

# Release v2.2.1

## GitHub release text

Magister School Integration v2.2.1 sluit omvangrijke attributen automatisch uit van de recorder-historie, zodat de 16 KB-waarschuwing verdwijnt zonder handmatige `recorder.exclude`.

### Nieuw

- **Recorder (#39)**: omvangrijke attributen worden nu via `_unrecorded_attributes` uitgesloten van de recorder-historie. De data blijft live beschikbaar voor card en templates; alleen de recorder slaat de historie niet meer op.

### Met dank aan

- @Niek (#39)

## HACS update text

Omvangrijke attributen worden automatisch uitgesloten van de recorder-historie (geen 16 KB-waarschuwingen meer, zonder handmatige configuratie).

## Previous release: v2.2.0

# Release v2.2.0

## GitHub release text

Magister School Integration v2.2.0 voegt volledige studiewijzer-teksten, correcte kindnamen met tussenvoegsel en uitval in de roosterwijzigingen toe.

### Nieuw
- **Studiewijzers (#41)**: volledige sectietekst i.p.v. previews, met behoud van lijstopmaak; gelijktijdige requests beperkt tot 4.
- **Kindnamen (#38)**: het `Tussenvoegsel` wordt nu meegenomen (bv. "Jan van Tilburg" i.p.v. "Jan Tilburg").
- **Uitval in wijzigingen (#37)**: vervallen lessen uit de afspraken worden nu ook aan de roosterwijzigingen toegevoegd.
- **Docs (#39)**: uitleg over de 16 KB recorder-limiet + `entity_globs` exclude-voorbeeld.

### Met dank aan
- @Niek (#41), @bassduh (#38), @Matthijsbr123 (#37), @barrymossel (#39)

## HACS update text

Volledige studiewijzer-teksten, Tussenvoegsel in kindnamen, uitval in roosterwijzigingen en verbeterde recorder-documentatie.

## Previous release: v2.1.1b0

# Release v2.0.6

## GitHub release text

Magister School Integration v2.0.6 fixes the homework counter: finished/unfinished homework is now read from the homework item's own `Afgerond` field instead of being derived from the (unrelated) assignments list.

### Fixes

- **Homework (#31)**: the homework sensor now counts finished vs unfinished homework using the `Afgerond` flag that Magister sends on each homework item. The previous version incorrectly derived "finished" by matching against submitted `opdrachten`, which is a different concept and is empty for most accounts.
- The overview sensor now also exposes `aantal_huiswerk_onafgerond` and `aantal_huiswerk_afgerond`, so cards can show both.

## HACS update text

Fixes the homework finished/unfinished counter: it now uses Magister's `Afgerond` field on the homework item itself.

## Previous release: v2.0.5

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
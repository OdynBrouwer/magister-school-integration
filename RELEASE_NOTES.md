# Release v2.4.1b0 (beta)

## GitHub release text

Magister School Integration v2.4.1b0 zorgt dat een **rate limit van Magister niet meer een hele verversing weggooit**. Alleen het verzoek dat geweigerd werd wacht en gaat daarna verder; de rest van de gegevens komt gewoon binnen.

### Opgelost

- **HTTP 429 zonder JSON-body werd niet herkend.** Magister kan een rate limit ook met een leeg antwoord en alleen een `Retry-After`-header terugsturen. Die reactie werd behandeld als "geen JSON-antwoord", waardoor de verversing zonder data verder liep. Nu wordt 429 altijd als rate limit herkend, ook zonder JSON.
- **`Retry-After` werd genegeerd.** Ontbreekt `secondsLeft` in het antwoord, dan wordt nu de `Retry-After`-header gebruikt in plaats van een vaste 17 seconden.

### Verbeterd

- **Alleen het geweigerde verzoek opnieuw.** Waar voorheen de hele fetch afbrak, wacht nu alleen dat ene verzoek tot de cooldown voorbij is en probeert het daarna opnieuw (maximaal 3 pogingen). De rest van de gegevens blijft binnenkomen.
- **Gedeelde cooldown.** Studiewijzer-onderdelen worden parallel opgehaald. Alle workers delen nu één cooldown met een lock, zodat ze Magister niet allemaal opnieuw lastigvallen tijdens dezelfde limiet.
- **Cooldown overleeft een re-login.** Wordt een gecachet token geweigerd en moet de integratie opnieuw inloggen, dan blijft de eerder opgelopen wachttijd gelden.
- **Nette grens aan het wachten.** De retry stopt na 65 seconden, binnen de 90-seconden-timeout van het subprocess. Duurt de cooldown langer, dan geeft de integratie het op zoals voorheen in plaats van te worden afgebroken door de timeout.

### Met dank aan

- **@Niek** ([#52](https://github.com/OdynBrouwer/magister-school-integration/pull/52)) — opnieuw een scherpe bijdrage: rate limits blokkeren de verversing niet meer en de cooldown wordt netjes gedeeld tussen parallelle verzoeken. 🙏

### Tests

- 6 nieuwe tests in `test_timeout_recovery.py`: een 200-met-`secondsLeft`, een 429 met alleen `Retry-After`, het delen van de cooldown tussen workers en het respecteren van de deadline. Totaal nu 246 tests.

### HACS update text

Beta: een rate limit van Magister gooit niet langer een hele verversing weg — alleen het geweigerde verzoek wacht en hervat. 429 wordt nu ook zonder JSON-body herkend en `Retry-After` wordt gebruikt. Met dank aan @Niek.

## Previous release: v2.4.0

# Release v2.4.0

## GitHub release text

Magister School Integration v2.4.0 voegt **berichten** en **mededelingen** toe: twee sensoren die laten zien of er iets nieuws van school is. Daarnaast is het inloggen robuuster geworden voor accounts met meerdere gebruikers of een passkey.

### Nieuw

- **`sensor.magister_data_ongelezen_berichten`** — aantal ongelezen berichten over alle mappen. Attributen: `mappen` (per map de telling) en `laatste` (de vijf nieuwste berichten met onderwerp, afzender, datum, gelezen-status en of er bijlagen zijn).
- **`sensor.magister_data_mededelingen`** — aantal mededelingen van school, met attribuut `laatste`.
- Nieuwe API-calls in `magister.py`: `berichten`, `berichten/mappen/alle`, `berichten/mappen/{id}/berichten` en `mededelingen`. Die horen bij het account, niet bij een kind.

### Verbeterd

- **Accountkeuze (`userselector`)** — hoort één login bij meerdere gebruikers, dan kiest de integratie automatisch het juiste account. Voorheen stopte de login met `Unhandled login action: 'userselector'`.
- **Passkey-promo voorkómen** — bij de wachtwoordstap worden `userSkippedFido` en `userWantsToPairSoftToken` meegestuurd, zoals de Magister-webapp doet, zodat de promo in één keer overgeslagen wordt.
- **Verlopen sessie** — een `Invalid Operation`-antwoord wordt nu ook als verlopen sessie herkend en automatisch hersteld.
- **Stille debuguitvoer** — een ontbrekende gebruikersnaam wordt als `?` gelogd in plaats van `None`.
- **Typefouten opgeruimd** — de integratie is statisch type-schoon (Pylance/pyright), zonder gedragswijziging.

### Ontwikkelhulpmiddelen (niet meegeleverd met HACS)

- `tools/magister_api_diff.py` — vergelijkt twee `--dump-raw`-snapshots en toont nieuwe, verdwenen en van type veranderde velden.
- `tools/magister_bundle_diff.py` — scant de openbare Magister-bundels op API-paden, OIDC-scopes, login-acties en feature-vlaggen.
- Beide staan in de map `tools/`; HACS installeert alleen `custom_components/magister_school/`.

### Privacy

Alleen de **telling** komt in de recorder-historie. Onderwerp en afzender staan in attributen die via `_unrecorded_attributes` buiten de historie blijven. Ontbrekende of onverwachte velden leveren geen crash maar een lege waarde.

### HACS update text

Nieuwe sensors voor ongelezen berichten en mededelingen, met de nieuwste berichten als attribuut. Alleen de telling wordt opgeslagen in de historie. Daarnaast robuuster inloggen bij accountkeuze en passkey-promo.

## Previous release: v2.4.0b0

# Release v2.4.0b0 (beta)

## GitHub release text

Magister School Integration v2.4.0b0 voegt twee nieuwe rubrieken toe: **berichten** en **mededelingen**. Dit is de eerste uitbreiding die uit de API-verkenning kwam — beide endpoints werken met een gewoon leerlingaccount.

### Nieuw

- **`sensor.magister_data_ongelezen_berichten`** — aantal ongelezen berichten over alle mappen. Attributen: `mappen` (per map de telling) en `laatste` (de vijf nieuwste berichten met onderwerp, afzender, datum, gelezen-status en of er bijlagen zijn).
- **`sensor.magister_data_mededelingen`** — aantal mededelingen van school, met attribuut `laatste`.
- Nieuwe API-calls in `magister.py`: `berichten` (hub), `berichten/mappen/alle`, `berichten/mappen/{id}/berichten` en `mededelingen`. Deze horen bij het account, niet bij een kind, dus de sensors zijn account-breed.
- **8 tests** in `test_postvak.py` voor het samentellen van ongelezen, het sorteren op datum, het afkappen op vijf, afzender als object én als tekst, en het melden van ontbrekende collecties.

### Privacy

Alleen de **telling** komt in de recorder-historie. Onderwerp en afzender staan in attributen die via `_unrecorded_attributes` buiten de historie blijven. Ontbrekende of onverwachte velden leveren geen crash maar een lege waarde.

### HACS update text

Beta: nieuwe sensors voor ongelezen berichten en mededelingen, met de nieuwste berichten als attribuut. Alleen de telling wordt opgeslagen in de historie.

## Previous release: v2.3.3b6

# Release v2.3.3b6 (beta)

## GitHub release text

Magister School Integration v2.3.3b6 breidt de bundelscan uit met de feature-vlaggen van Magister zelf, en legt vast waarom er géén links-crawler komt.

### Nieuw

- **`settings.js` als signaal** — de per-school instellingenpagina van de webapp bevat `featureFlags` (`enableOPP`, `m6LoggingEnabled`, …) en de hostnames van de producten die een school mag gebruiken (`opp`, `attendance`, `lockers`, `learningmaterials`, `calendar`). `tools/magister_bundle_diff.py` legt die nu vast in de `config`-bucket, zodat "Magister zet een nieuw product aan" als verschil opduikt.
- `extract_config` is niet meer regelgebaseerd: ook éénregelige/minified config wordt gelezen, inclusief `window.location.origin`-samenstellingen.
- **2 nieuwe tests** in `test_bundle_diff.py` (feature-vlaggen uit `settings.js`, en `collect_sources` die de bucket aanmaakt).

### Onderzocht, niet gebouwd

Met een leerlingaccount is de hypermedia-link-graaf gemeten: alleen de cijfers-endpoints leveren `Links`, samen 5 bereikbare endpoints waarvan 3 nieuw (`cijfers/perioden/{id}`, `cijfers/werkinformatie/{id}`, `leerlingen/{id}/cijfers/kolommen/{id}/gerelateerdekolommen`), en `/api/sessies/current` bestaat niet voor een leerling. Een links-crawler zou dus nauwelijks iets toevoegen; daarom is die geschrapt.

### HACS update text

Beta: bundelscan legt nu ook Magister's feature-vlaggen en product-hostnames vast. Aan de integratie zelf verandert niets.

## Previous release: v2.3.3b5

# Release v2.3.3b5 (beta)

## GitHub release text

Magister School Integration v2.3.3b5 voegt een tweede hulpmiddel toe dat nieuwe Magister-functies opspoort — deze keer ook compleet nieuwe rubrieken, en zonder dat er een account voor nodig is.

### Nieuw

- **`tools/magister_bundle_diff.py`** — scant de openbare JavaScript-bundels van de Magister-webapp (`/magister/`, `/op/`, `oidc_config.js` en de loginbundle) en vergelijkt die met een baseline. Wat eruit komt: alle `/api/...`-paden (61 stuks bij de laatste meting), alle OIDC-`scopes` (= de feature-lijst van Magister) en alle `action:`-waarden uit de loginflow (14 stappen).
- Een nieuwe scope of een nieuw API-pad betekent vrijwel altijd een nieuwe functie. Bestandsnamen met content-hash (`app.<hash>.js`) en id's in het pad worden genormaliseerd, zodat een nieuwe build geen ruis geeft.
- **`test_bundle_diff.py`** — 12 tests voor normalisatie, het filteren van ruis, scope/config-parsing, het diffen en de exitcodes.

### Documentatie

- README-sectie **Magister-API in de gaten houden** is gesplitst in twee hulpmiddelen: bestaande data wijzigt (`magister_api_diff.py`, met account) en nieuwe rubrieken/loginwijzigingen (`magister_bundle_diff.py`, zonder account).
- Vastgelegd dat `tools/` ontwikkelgereedschap is: HACS installeert alleen `custom_components/magister_school/`, dus deze scripts worden nooit meegeleverd.

### HACS update text

Beta: nieuw ontwikkelhulpmiddel dat nieuwe Magister-functies detecteert via de openbare webapp-bundels. Aan de integratie zelf verandert niets.

## Previous release: v2.3.3b4

# Release v2.3.3b4 (beta)

## GitHub release text

Magister School Integration v2.3.3b4 voegt een hulpmiddel toe om API-wijzigingen bij Magister te zien vóórdat ze de integratie breken.

### Nieuw

- **`tools/magister_api_diff.py`** — vergelijkt twee `--dump-raw`-snapshots en toont per endpoint welke velden erbij kwamen (`+`), verdwenen (`-`) of van type veranderden (`~`), plus endpoints die maar in één dump voorkomen. Query-strings en getallen in het pad worden genegeerd, zodat een andere datum of leerling-id geen ruis geeft. `--json` geeft een machineleesbaar rapport; de exitcodes 0/1/2 maken het bruikbaar in een cronjob of GitHub Action.
- **`test_api_diff.py`** — 9 tests voor de normalisatie, het flatten van responses, toegevoegde/verdwenen/type-gewijzigde velden en de exitcodes.

### Documentatie

- README-sectie **Magister-API in de gaten houden**: hoe je een nulmeting maakt en die later vergelijkt.

### HACS update text

Beta: nieuw ontwikkelhulpmiddel dat API-wijzigingen bij Magister detecteert. Aan de integratie zelf verandert niets.

## Previous release: v2.3.3b3

# Release v2.3.3b3 (beta)

## GitHub release text

Magister School Integration v2.3.3b3 is een kleine opruimversie: de accountkeuze-logregel toont geen `None` meer.

### Aangepast

- Bij het loggen van de accountkeuze (`--debug`, buiten JSON-modus) wordt een ontbrekende gebruikersnaam nu als `?` weergegeven in plaats van `None`.
- Geen gedragswijziging: de integratie draait altijd met `--json`, waarbij deze logregel niet uitgevoerd wordt.

### HACS update text

Beta: alleen opschoning van de debuguitvoer bij de accountkeuze; geen gedragswijziging.

## Previous release: v2.3.3b2

# Release v2.3.3b2 (beta)

Magister School Integration v2.3.3b2 ondersteunt alle aanmeldstappen die Magister tijdens het inloggen kan terugsturen.

### Nieuw

- **Accountkeuze (`userselector`)** — als één login aan meerdere gebruikers is gekoppeld, kiest de integratie automatisch het account dat bij de ingevoerde gebruikersnaam hoort (anders het eerste). Voorheen stopte de login met `Unhandled login action: 'userselector'`.
- **Passkey-promo voorkómen** — bij de wachtwoordstap worden nu `userSkippedFido` en `userWantsToPairSoftToken` meegestuurd, zoals de Magister-webapp doet. De promo wordt daarmee in één keer overgeslagen in plaats van achteraf.
- **Meerdere tussenstappen** — promo en accountkeuze worden herhaald afgehandeld, ook ná de 2FA-stap.

### Documentatie

- README heeft een sectie **Aanmeldmethoden** met wat wel en niet kan (wachtwoord, TOTP, accountkeuze vs. passkey, hardwaretoken, herstelcode en SSO).

### HACS update text

Beta: ondersteuning voor Magister's accountkeuze bij meerdere gebruikers, passkey-promo wordt direct overgeslagen, en de README documenteert welke aanmeldmethoden werken.

## Previous release: v2.3.3b1

# Release v2.3.3b1 (beta)

Magister School Integration v2.3.3b1 ruimt alle statische typefouten op die Pylance in de code aangaf. Er verandert niets aan het gedrag; de bestanden zijn type-schoon.

### Opgelost

- `import urllib.error` toegevoegd; `urllib.error` werd alleen indirect via `urllib.request` geladen, waardoor Pylance het submodule niet zag.
- `handlers` in de HTTP-opener is nu getypeerd als `list[urllib.request.BaseHandler]`.
- `httpreq()`, `httpredirurl()` en `_read_response()` hebben expliciete return-types.
- De hergebruikte variabele `d` in de loginflow is gesplitst; de URL-fragment-parameters heten nu `fragments`.
- `store_access_token()` en `invalidate_access_token()` accepteren `str | Path`.
- `totp_secret` en `history_file` zijn expliciet `str | None` in plaats van impliciet optionaal.
- De 503-detectie gebruikt nu één `re.search`-resultaat in plaats van twee losse aanroepen.

### HACS update text

Beta: codeopruiming zonder gedragswijziging — alle Pylance-typefouten in het Magister-script en de integratie zijn opgelost.

## Previous release: v2.3.3b0

# Release v2.3.3b0 (beta)

Magister School Integration v2.3.3b0 herkent het antwoord dat Magister geeft bij een verlopen of geweigerd sessietoken nu correct als "sessie verlopen", in plaats van als een kapot account.

### Aanleiding

Een live controle van de Magister-API liet zien dat `GET /api/account` met een ongeldig token antwoordt met **HTTP 400** en de body `"Invalid Operation"`. De integratie behandelde dat als "geen JSON-antwoord", waarna de melding *"account response has no valid person ID"* verscheen. Dat is precies de verwarrende melding die tijdens de storing van 23/24 november als eerste in het log stond.

### Opgelost

- Zowel `SecurityToken Expired` als `Invalid Operation` (bytes en string, hoofdletterongevoelig) geldt nu als verlopen sessie.
- Daardoor wordt meteen het bestaande herstelpad gebruikt: token weggooien, opnieuw inloggen en de aanvraag herhalen.
- Het log noemt de juiste oorzaak in plaats van een misleidende accountfout.

### HACS update text

Beta: herkent Magister's `"Invalid Operation"`-antwoord (HTTP 400) als verlopen sessie, zodat de integratie opnieuw inlogt in plaats van een accountfout te melden.

## Previous release: v2.3.2

# Release v2.3.2

Magister School Integration v2.3.2 bundelt alle fixes uit de bètareeks: de 2FA-passkeypromo wordt nu ook na de soft-tokenstap overgeslagen, een verlopen sessietoken wordt eenmalig vernieuwd, een tijdelijke Magister-storing is duidelijk zichtbaar als melding, rate limits worden gerespecteerd, en de meegeleverde kaart krijgt instelbare hoogtes plus een correcte cache-versie.

### Nieuw: blueprints

De repository bevat nu twee blueprints: een meldingsblueprint (lesuitval, huiswerk, cijfers, absenties, roosterwijzigingen) en een dagelijks overzicht. Beide werken per kind en melden alleen nieuwe items.

### Opgelost

- **2FA-passkeypromo na de soft-tokenstap (#46)** — Magister kan de passkeypromo ook na de 2FA-stap tonen; die wordt nu op beide plekken overgeslagen.
- **Verlopen sessietoken** — een gecachet token dat door `/api/account` wordt geweigerd, wordt eenmalig verwijderd, waarna opnieuw wordt ingelogd en de aanvraag opnieuw wordt gedaan.
- **Duidelijke storingsmelding** — HTTP 502/503/504 verschijnt als reparatiemelding "Magister is tijdelijk niet beschikbaar", met de uitleg dat het bij Magister/Trevianum zit en niet bij de integratie. De melding verdwijnt zodra er weer data is.
- **Rate limits (#51)** — JSON-429-antwoorden worden centraal herkend; de retry wacht op `secondsLeft` (1-300 s) en gedeeltelijke studiewijzerdata wordt niet meer als volledige fetch gepubliceerd.
- **Meerdere accounts (#50)** — de registratie van de meegeleverde kaart is geserialiseerd, zodat een tweede configuratie-entry niet meer stukloopt op een dubbele route.
- **Widgethoogte (#49)** — de kaart ondersteunt `widget_height` en `widget_heights`, inclusief `auto` voor volledige hoogte zonder interne scrollbar.
- **Kaartcache** — een bestaande Lovelace-resource wordt bijgewerkt naar de actuele versie in plaats van een oude `?v=`-URL te houden.
- **Foutdiagnostiek** — onverwachte scriptfouten komen nu ook in het Home Assistant-log, niet alleen in `/config/magister_error.log`.

### HACS update text

Stabiele release met alle bètafixes: 2FA-passkeypromo na de soft-tokenstap, herstel van verlopen sessies, duidelijke Magister-storingsmelding, rate-limit-afhandeling, multi-account-kaartfix, instelbare widgethoogtes en correcte kaartcache-versie. Inclusief twee blueprints.

## Previous release: v2.3.2b6

# Release v2.3.2b6 (beta)

## GitHub release text

Magister School Integration v2.3.2b6 fixes bundled-card cache updates and card sizing.

### Fixes

- Existing Lovelace resource entries are updated to the current manifest/card version instead of keeping an old `?v=` URL.
- The card exposes `getCardSize()` and `getGridOptions()` for configurable dashboard height.
- Full-height and per-widget height options remain available through `widget_height` and `widget_heights`.

## Previous release: v2.3.2b5

# Release v2.3.2b5 (beta)

## GitHub release text

Magister School Integration v2.3.2b5 fixes duplicate bundled-card registration during multi-account startup and adds configurable widget heights to the dashboard card.

### Fixes

- Card static-path and Lovelace-resource registration is serialized for multiple Magister config entries (#50).
- The card accepts `widget_height` for all widgets and `widget_heights` for individual widgets (#49).
- Use `widget_height: auto` or `widget_height: null` to remove the default internal scrollbar height.
- Use `widget_heights: {rooster_vandaag: auto, huiswerk: 600}` for per-widget control.

### HACS update text

Beta fix for duplicate card startup registration and new configurable card/widget heights.

## Previous release: v2.3.2b4

# Release v2.3.2b4 (beta)

## GitHub release text

Magister School Integration v2.3.2b4 handles Magister HTTP 429 rate-limit responses centrally. The retry uses the reset time reported by Magister, and incomplete/rate-limited study-guide fetches are not published as successful full data.

### Fixes

- Recognizes JSON 429 responses centrally.
- Honors `secondsLeft` with a bounded retry delay of 1-300 seconds.
- Prevents partial/rate-limited study-guide data from replacing the last successful data.
- Keeps the existing temporary 502/503/504 outage handling.

### HACS update text

Beta fix for Magister rate limits: HTTP 429 responses wait for the reported reset time and avoid publishing incomplete study-guide data.

## Previous release: v2.3.2b3

# Release v2.3.2b3 (beta)

## GitHub release text

Magister School Integration v2.3.2b3 makes temporary Magister server outages clear to users: HTTP 502, 503 and 504 are shown as "Magister is temporarily unavailable" instead of as a generic integration setup failure.

### Fixes

- Adds a dedicated Home Assistant repair issue for temporary Magister outages.
- Keeps automatic retries active.
- Clears the outage issue automatically when Magister data returns.

### HACS update text

Beta fix for Magister outages: temporary HTTP 502/503/504 responses now clearly say that Magister or Trevianum is unavailable, rather than blaming the integration.

## Previous release: v2.3.2b2

# Release v2.3.2b2 (beta)

## GitHub release text

Magister School Integration v2.3.2b2 treats Magister HTTP 502, 503 and 504 responses as temporary server failures instead of permanent setup or account failures.

### Fixes

- Temporary Magister server failures use the existing two-attempt retry flow.
- HTTP 503 no longer immediately marks the integration setup as failed.

### HACS update text

Beta fix for Magister temporary 502/503/504 responses: retries the Magister fetch instead of treating it as a permanent account failure.

## Previous release: v2.3.2b1

# Release v2.3.2b1 (beta)

## GitHub release text

Magister School Integration v2.3.2b1 improves script error reporting. Unexpected Magister script exceptions are now included in the Home Assistant log instead of only in `/config/magister_error.log`.

### Fixes

- Unexpected script exceptions are printed to stderr and remain available in `/config/magister_error.log`.
- Empty script stderr output gets a clear fallback mentioning `/config/magister_error.log`.

### HACS update text

Beta diagnostic update: unexpected Magister script failures now show their real exception in the Home Assistant log.

## Previous release: v2.3.2b0

# Release v2.3.2b0 (beta)

## GitHub release text

Magister School Integration v2.3.2b0 fixes failed API refreshes after a Magister session token expires. A stale cached token is removed once, the integration logs in again, and the account API is retried automatically.

### Fixes

- **2FA passkey promo (#46)**: Magister's passkey-proposal step is now skipped after both the password step and the 2FA soft-token step.
- Cached access tokens are invalidated and refreshed once after `/api/account` rejects them.
- HTTP 401/403 responses are reported as authorization failures.
- HTTP 5xx responses are reported as Magister server failures.
- Non-JSON authorization and server responses no longer get confused with normal API data.

### HACS update text

Beta fix for failed Magister API refreshes after an expired session token: the stale cache is refreshed once and the account request is retried.

## Previous release: v2.3.1

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
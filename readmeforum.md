# 🎉 Magister School Integration v1.0.8 Release

## Nederlands

Hallo allemaal!

Ik ben blij om **versie 1.0.8** aan te kondigen met belangrijke verbeteringen rondom authenticatie en her-authenticatie!

### ✨ Wat is er nieuw?

#### 🔄 Re-authenticatie & meldingen
- Detectie wanneer Magister een wachtwoordwijziging of extra authenticatie vereist.
- Home Assistant toont nu een **persistente melding**: "Mogelijk nieuw wachtwoord nodig voor Magister."
- Re-auth flow toegevoegd zodat je **direct een nieuw wachtwoord kunt invoeren** zonder de integratie te verwijderen.

#### 🔧 Overige fixes
- `.gitignore` toegevoegd (o.a. `venv/` en `test_output.txt`) om tijdelijke bestanden te negeren.

--- 

# 🎉 Magister School Integration v1.0.7 Release

## Nederlands

Hallo allemaal!

Ik ben blij om **versie 1.0.7** aan te kondigen met twee belangrijke nieuwe features!

### ✨ Wat is er nieuw?

#### 👤 Student Account Support
Studenten kunnen nu de integratie gebruiken met hun eigen credentials! Voorheen werkte de integratie alleen met ouder-accounts. Nu detecteert de integratie automatisch of je met een student account inlogt en toont dan de data van de ingelogde student zelf.

**Hoe werkt het?**
- Student logt in met eigen Magister credentials
- Integratie detecteert automatisch dat het een student account is
- Creëert één 'kind' entry met de eigen data van de student
- Alle sensors (cijfers, rooster, huiswerk, etc.) werken gewoon!

#### 🔐 Multi-Account Cache Fix
Een kritieke fix voor wie meerdere Magister accounts in Home Assistant gebruikt. Voorheen overschreven verschillende accounts elkaars access tokens, wat leidde tot "Invalid Operation" errors.

**Wat is er veranderd?**
- Elke account krijgt nu zijn eigen cache file: `.magister_auth_cache_<schoolserver>_<username>`
- Speciale karakters (@, ., /) worden automatisch gesanitized naar underscores
- Backward compatible - oude setups blijven gewoon werken
- Nu kun je bijvoorbeeld een student account én een ouder account tegelijk gebruiken!

### 🧪 Uitgebreid Getest

De release is uitgebreid getest met:
- ✅ Student accounts (esloo.magister.net)
- ✅ Ouder accounts met meerdere kinderen (trevianum.magister.net)
- ✅ Meerdere accounts die tegelijk draaien
- ✅ Token caching en hergebruik

### 📦 Installatie/Update

**Via HACS (aanbevolen):**
1. Ga naar HACS → Integrations
2. Zoek "Magister School Integration"
3. Klik op "Update"
4. Herstart Home Assistant

**Handmatig:**
Download de release van [GitHub](https://github.com/OdynBrouwer/magister-school-integration/releases/tag/v1.0.7)

### 🔗 Links

- [GitHub Repository](https://github.com/OdynBrouwer/magister-school-integration)
- [Release v1.0.7](https://github.com/OdynBrouwer/magister-school-integration/releases/tag/v1.0.7)
- [Changelog](https://github.com/OdynBrouwer/magister-school-integration/compare/v1.0.6...v1.0.7)

### 💬 Feedback

Zoals altijd: feedback, bug reports en feature requests zijn welkom in de [GitHub Issues](https://github.com/OdynBrouwer/magister-school-integration/issues)!

Veel plezier met de update! 🚀

---

## English

Hello everyone!

I'm excited to announce **version 1.0.7** with two important new features!

### ✨ What's New?

#### 👤 Student Account Support
Students can now use the integration with their own credentials! Previously, the integration only worked with parent accounts. Now the integration automatically detects when you log in with a student account and displays the data of the logged-in student.

**How does it work?**
- Student logs in with their own Magister credentials
- Integration automatically detects it's a student account
- Creates a single 'child' entry with the student's own data
- All sensors (grades, schedule, homework, etc.) work normally!

#### 🔐 Multi-Account Cache Fix
A critical fix for those using multiple Magister accounts in Home Assistant. Previously, different accounts would overwrite each other's access tokens, leading to "Invalid Operation" errors.

**What changed?**
- Each account now gets its own cache file: `.magister_auth_cache_<schoolserver>_<username>`
- Special characters (@, ., /) are automatically sanitized to underscores
- Backward compatible - existing setups continue to work
- You can now use a student account and a parent account simultaneously!

### 🧪 Extensively Tested

This release has been thoroughly tested with:
- ✅ Student accounts (esloo.magister.net)
- ✅ Parent accounts with multiple children (trevianum.magister.net)
- ✅ Multiple accounts running simultaneously
- ✅ Token caching and reuse

### 📦 Installation/Update

**Via HACS (recommended):**
1. Go to HACS → Integrations
2. Search for "Magister School Integration"
3. Click "Update"
4. Restart Home Assistant

**Manual:**
Download the release from [GitHub](https://github.com/OdynBrouwer/magister-school-integration/releases/tag/v1.0.7)

### 🔗 Links

- [GitHub Repository](https://github.com/OdynBrouwer/magister-school-integration)
- [Release v1.0.7](https://github.com/OdynBrouwer/magister-school-integration/releases/tag/v1.0.7)
- [Changelog](https://github.com/OdynBrouwer/magister-school-integration/compare/v1.0.6...v1.0.7)

### 💬 Feedback

As always: feedback, bug reports, and feature requests are welcome in the [GitHub Issues](https://github.com/OdynBrouwer/magister-school-integration/issues)!

Enjoy the update! 🚀

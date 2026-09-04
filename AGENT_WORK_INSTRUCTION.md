# Octopus Energy DE – Agent Work Instruction

## Zweck

Dieses Dokument ist die verbindliche Arbeitsanweisung für Coding-Agenten, die am Repository `octopus_energy_de` arbeiten.

Repository:

```text
https://github.com/thecem/octopus_energy_de
```

Home-Assistant-Domain:

```text
custom_components/octopus_energy_de/
```

Ziel ist eine langfristig wartbare, modulare Home-Assistant-Integration für Octopus Energy Deutschland. Die Integration darf **nicht** wieder zu einem Monolithen wie die alte `octopus_germany`-Integration werden.

Dieses Dokument ist gleichzeitig Architekturvorgabe, Review-Checkliste, Arbeitsauftrag, Agent-Prompt und Definition of Done.

---

## 1. Grundarchitektur

```text
Kraken GraphQL API
        |
        v
api/
        |
        v
mappers/
        |
        v
models/
        |
        +------------------+
        |                  |
        v                  v
tariffs/            capabilities/
                        smartflex/
        |                  |
        +--------+---------+
                 |
                 v
           coordinators/
                 |
                 v
             entities/
                 |
                 v
          Home Assistant
```

Home-Assistant-Entities dürfen keine rohe Kraken-/GraphQL-Struktur interpretieren.

---

## 2. Wichtigste Architekturregel

### Niemals Marketingname mit technischer Preislogik gleichsetzen

Falsch:

```python
if "GO" in product_code:
    calculate_go_price()

if "HEAT" in product_code:
    calculate_heat_price()
```

Richtig:

```text
API-Struktur
    |
    v
technischer Tariftyp
    |
    v
generischer Handler
```

Beispiel:

```text
Octopus Go
    family = OCTOPUS_GO
    pricing_model = TIME_OF_USE
```

```text
Octopus Heat
    family = OCTOPUS_HEAT
    pricing_model = TIME_OF_USE
```

Beide verwenden denselben generischen `TimeOfUseTariffHandler`.

---

## 3. Tarifmodell

Mindestens folgende technischen Tariftypen müssen getrennt von Marketingnamen existieren:

```text
FIXED
TIME_OF_USE
DYNAMIC
UNKNOWN
```

Produktfamilien sind davon getrennt:

```text
GENERIC_FIXED
OCTOPUS_GO
OCTOPUS_HEAT
DYNAMIC_OCTOPUS
INTELLIGENT_OCTOPUS
INTELLIGENT_OCTOPUS_GO_LEGACY
FAN_CLUB
SOLAR_UP
POWER_DRIVE
ZERO_BILLS
UNKNOWN
```

Neue `TariffType`-Werte nur einführen, wenn wirklich ein neuer technischer Preisalgorithmus notwendig ist.

Langfristig drei Dimensionen unterstützen:

```text
Pricing Model
+
Product Family
+
Capabilities / Pricing Modifiers
```

Beispiele:

```text
SolarUp
pricing_model = FIXED
family = SOLAR_UP
capabilities = EXPORT + BATTERY + SOLAR
```

```text
Fan Club
pricing_model = API-dependent
family = FAN_CLUB
modifiers = WIND_DISCOUNT
```

```text
Intelligent Octopus
pricing_model = API-dependent
family = INTELLIGENT_OCTOPUS
capabilities = SMARTFLEX + EV / BATTERY
```

**SmartFlex ist keine Tarifart.**

---

## 4. Vor jeder Änderung aktuellen Repo-Stand prüfen

Mindestens prüfen:

```text
sensor.py
services.py
coordinator.py
manifest.json
config_flow.py
SUPPORTED_TARIFFS.md
ROADMAP.md
ARCHITECTURE.md
README.md
tests/
.github/workflows/
```

Der vorhandene Funktionsumfang darf bei Refactorings nicht verloren gehen, insbesondere:

```text
Login
Account Discovery
Fixed
Time-of-Use
Dynamic
SmartFlex
Smart Control
Boost
Device Preferences
Consumption Services
CSV Export
Coordinatoren
```

---

## 5. Bekannte aktuelle Baustellen

### 5.1 Manifest-URLs

Das Repository heißt:

```text
thecem/octopus_energy_de
```

Alle `documentation`, `issue_tracker`, README- und GitHub-Links müssen exakt auf diesen Repository-Namen zeigen. Keine alte Variante wie `octopus-energy-de` verwenden.

### 5.2 Dokumentation

Nach jedem Release konsistent halten:

```text
README.md
ARCHITECTURE.md
ROADMAP.md
SUPPORTED_TARIFFS.md
RELEASE_NOTES.md
manifest.json
```

Keine veralteten Hinweise stehen lassen, wenn Features bereits implementiert sind.

### 5.3 Monolithen verhindern

Besonders beobachten:

```text
sensor.py
services.py
coordinator.py
client.py
```

Wenn eine Datei mehrere fachlich unabhängige Verantwortlichkeiten enthält, aufteilen.

---

## 6. Zielstruktur

```text
custom_components/octopus_energy_de/
|
├── __init__.py
├── manifest.json
├── config_flow.py
├── const.py
|
├── api/
│   ├── client.py
│   ├── auth.py
│   ├── exceptions.py
│   ├── graphql/
│   │   ├── account.py
│   │   ├── tariffs.py
│   │   ├── meters.py
│   │   ├── consumption.py
│   │   └── smartflex.py
│   ├── mappers/
│   │   ├── account.py
│   │   ├── tariff.py
│   │   ├── rate.py
│   │   ├── meter.py
│   │   └── smartflex.py
│   └── models/
│       ├── account.py
│       ├── tariff.py
│       ├── rate.py
│       ├── meter.py
│       ├── device.py
│       ├── dispatch.py
│       └── session.py
|
├── tariffs/
│   ├── types.py
│   ├── detector.py
│   ├── registry.py
│   ├── fixed.py
│   ├── time_of_use.py
│   ├── dynamic.py
│   └── unknown.py
|
├── capabilities/
│   └── smartflex/
│       ├── devices.py
│       ├── dispatches.py
│       ├── sessions.py
│       ├── preferences.py
│       ├── control.py
│       └── boost.py
|
├── coordinators/
│   ├── account.py
│   ├── tariff.py
│   ├── meter.py
│   ├── consumption.py
│   └── smartflex.py
|
├── entities/
│   ├── electricity/
│   │   ├── current_rate.py
│   │   ├── next_rate.py
│   │   ├── tariff.py
│   │   ├── meter_reading.py
│   │   └── consumption.py
│   ├── smartflex/
│   │   ├── state.py
│   │   ├── state_of_charge.py
│   │   ├── active_power.py
│   │   ├── dispatching.py
│   │   └── sessions.py
│   └── gas/
|
├── actions/
│   ├── preferences.py
│   ├── consumption.py
│   └── export.py
|
├── sensor.py
├── binary_sensor.py
├── switch.py
├── number.py
├── time.py
├── button.py
└── diagnostics.py
```

Nicht alles muss sofort verschoben werden; dies ist das Zielbild.

---

## 7. Thin Entity Rule

Entities dürfen HA-State, Attribute, DeviceInfo und Delegation enthalten.

Sie dürfen **nicht**:

```text
GraphQL parsen
Tariftypen erkennen
Zeitfenster berechnen
API Payloads normalisieren
Authentifizierung durchführen
SmartFlex fachlich auswerten
```

Falsch:

```python
product = coordinator.data["product"]
if product["unitRateInformation"]["__typename"] == "...":
    ...
```

Richtig:

```python
tariff = coordinator.data.tariff
rate = tariff_service.current_rate(tariff, now)
```

---

## 8. GraphQL-Regel

GraphQL Query Strings gehören nach:

```text
api/graphql/
```

API/Mapper dürfen Kraken-Struktur kennen. Domain- und Entity-Schicht nicht.

---

## 9. Domain Models

Rohe Dictionaries früh in typisierte Models übersetzen:

```text
Rate
Tariff
Account
ElectricitySupply
GasSupply
Meter
MeterReading
SmartFlexDevice
Dispatch
ChargingSession
```

Beispiel:

```python
@dataclass(frozen=True)
class Rate:
    value: Decimal
    valid_from: datetime
    valid_to: datetime
    name: str | None
```

---

## 10. Keine festen 15/30/60-Minuten-Annahmen

Falsch:

```python
timedelta(minutes=15)
```

als Tariflogik.

Richtig:

```python
rate.valid_from <= now < rate.valid_to
```

Die API ist die Wahrheit über das Intervall.

---

## 11. Time-of-Use-Regel

Go und Heat generisch verarbeiten.

Keine hardcodierten Uhrzeiten, wenn Kraken `timeslotActivationRules` liefert.

Wenn reale API-Struktur nicht ausreicht: nicht raten, sondern `UNKNOWN`, Diagnostics oder Fixture anfordern.

---

## 12. SmartFlex-Regel

SmartFlex ist Capability, nicht `TariffType`.

Bereiche:

```text
Devices
Device State
State of Charge
Active Power
Dispatches
Charging Sessions
Preferences
Smart Control
Boost
```

Fachlogik nach:

```text
capabilities/smartflex/
```

Sinnvolle native HA-Entities:

```text
binary_sensor.<device>_dispatching
sensor.<device>_next_dispatch_start
sensor.<device>_next_dispatch_end
sensor.<device>_dispatch_energy
number.<device>_target_soc
time.<device>_target_time
```

Boost-Semantik anhand realer API prüfen: `switch` versus `button.start_boost` / `button.cancel_boost` + Statussensor.

---

## 13. Dynamische Entity Discovery

SmartFlex-Devices können nach dem Setup hinzukommen oder verschwinden.

Unterstützen:

```text
Device added
Device removed
Device type changed
```

Mögliche Mechanismen:

```text
dispatcher signal
coordinator listener
dynamic async_add_entities
config entry reload als Fallback
```

Bevorzugt ohne manuellen Reload.

---

## 14. Diagnostics

`diagnostics.py` ist Pflicht vor v1.0.

Anonymisieren/entfernen:

```text
email
password
token
account number
MALO
MELO
meter serial
meter ID
device ID
property ID
name
address
postal code
vehicle identifiers
```

Erhalten, soweit nicht personenbezogen:

```text
product code
product fullName
product description
isTimeOfUse
GraphQL typename
unit rate structures
forecast structures
timeslot rules
capability structure
enum/state information
```

Nie komplette unbereinigte Kraken-Antworten loggen.

---

## 15. Reauthentication

Config Flow muss unterstützen:

```python
async_step_reauth()
async_step_reauth_confirm()
```

Passwortänderung darf kein Löschen und Neuanlegen der Integration erfordern.

---

## 16. Options Flow

Sinnvolle Optionen:

```text
SmartFlex enabled
Historical consumption enabled
Diagnostics detail
Polling intervals
```

Nicht jede interne Einstellung konfigurierbar machen.

---

## 17. Energy Dashboard / Statistics

Historische Verbrauchswerte nicht als Sensor pro Intervall modellieren.

Bevorzugt:

```text
Home Assistant long-term statistics
Energy Dashboard compatible statistics
```

Import und Export getrennt behandeln.

---

## 18. Gas

Gas direkt modular einführen:

```text
api/models/gas.py
api/mappers/gas.py
coordinators/gas.py
entities/gas/
```

Modelle z. B.:

```text
GasSupply
GasContract
GasMeter
GasRate
GasMeterReading
```

---

## 19. Solar / Export / Zero Bills

Für SolarUp, Zero Bills etc. langfristig getrennte Modelle vorsehen:

```text
ExportAgreement
ExportRate
GenerationMeter
SolarAsset
BatteryAsset
AnnualAllowance
```

Import-Strompreis und Einspeisevergütung nicht in dasselbe Feld drücken.

---

## 20. Tarif-Inventar

`SUPPORTED_TARIFFS.md` ist verbindlich.

Pro Produkt mindestens:

```text
Marketing name
Known product code pattern
Publicly available?
Pricing model
Product family
SmartFlex?
Fixture available?
Tests available?
Support status
```

Statuswerte:

```text
SUPPORTED
CODE_READY
PARTIALLY_TESTED
LEGACY_SUPPORTED
DISCOVERED
UNKNOWN_API_STRUCTURE
```

Nur mit realer anonymisierter Kraken-Fixture oder vergleichbar belastbarer API-Struktur `SUPPORTED` setzen.

Priorität der Fixtures:

```text
1. Fixed
2. Octopus Go
3. Octopus Heat
4. dynamicOctopus
5. Intelligent Octopus Go 2024
6. aktuelles Intelligent Octopus + EV
7. aktuelles Intelligent Octopus + Battery
8. Fan Club
9. SolarUp
10. PowerDrive
11. Zero Bills
```

Bei unbekannter API-Struktur nicht raten.

---

## 21. Fixture Security

Vor Commit anonymisieren:

```text
account number
email
name
address
MALO
MELO
meter serial
meter ID
property ID
device ID
vehicle identifier
token
authorization header
```

Automatisierten CI-Test auf sensitive Muster einbauen, mindestens:

```text
@example.com
Authorization
Bearer
token
accountNumber
malo
melo
meterSerial
streetAddress
postalCode
password
```

---

## 22. Testanforderungen

Vor v1.0 mindestens:

```text
test_config_flow.py
test_reauth.py
test_init.py
test_coordinator.py
test_sensor.py
test_binary_sensor.py
test_switch.py
test_number.py
test_time.py
test_services.py
test_diagnostics.py
```

Domain-Tests:

```text
Fixed
TOU
Dynamic
Unknown
DST
Midnight
arbitrary interval length
empty rate list
missing forecast
null GraphQL values
unknown product
legacy Intelligent Go
```

Integrations-Level:

```text
Integration setup
Integration unload
Reload
Authentication failure
API timeout
GraphQL partial error
Multiple accounts
Multiple electricity supplies
Tariff changes while HA runs
SmartFlex becomes unavailable
Device added after startup
Device removed after startup
```

---

## 23. Zeitzonen / DST

Alle Rate-Zeitstempel timezone-aware.

Deutsche lokale Tarifregeln:

```text
Europe/Berlin
```

Tests für:

```text
Winter -> Sommerzeit
Sommer -> Winterzeit
repeated 02:xx hour
missing 02:xx hour
Midnight
```

---

## 24. Fehlerverhalten

Ein unbekannter Tarif darf die Integration nicht zerstören.

Statt Exception:

```text
TariffType.UNKNOWN
+
diagnostic metadata
+
warning log
+
best effort mapping, wenn sicher
```

Ein einzelner unbekannter Tarif darf nicht den gesamten Config Entry unbrauchbar machen.

---

## 25. API Rate Limits

Daten nach Änderungsfrequenz trennen:

```text
Account data         selten
Tariff data          mittel
Meter data           mittel
Consumption          on demand / passend
SmartFlex            häufiger
```

Keine unnötigen Polling-Schleifen in Entities.

---

## 26. Keine Endlosschleifen in Entities

Nicht:

```python
while True:
    await asyncio.sleep(30)
    self.async_write_ha_state()
```

Zeitbasierte Zustände gehören in Coordinator, Domain-Service oder HA-Scheduler.

---

## 27. Unique IDs

Refactorings dürfen bestehende Unique IDs nicht unnötig ändern.

Vor Änderung prüfen:

```text
entity_id
unique_id
device identifiers
config entry unique_id
```

Datei- oder Klassenwechsel darf keine neue Entity erzeugen.

---

## 28. Services vs native Entities

Wenn sinnvoll, native HA-Entity bevorzugen:

```text
number
time
button
switch
binary_sensor
sensor
```

Services für komplexe oder Batch-Aktionen verwenden.

---

## 29. CI und Repository-Qualität

Mindestens:

```text
pytest
ruff
hassfest
HACS validation
```

Zusätzlich sinnvoll:

```text
CodeQL
Dependabot
pre-commit
```

Branch Protection:

```text
PR required
CI required
no direct push to main
```

---

## 30. Dokumentation nach Änderungen

Bei Architektur- oder Nutzeränderungen im selben PR prüfen:

```text
README.md
ARCHITECTURE.md
ROADMAP.md
SUPPORTED_TARIFFS.md
RELEASE_NOTES.md
```

---

## 31. Empfohlene Release-Reihenfolge

### v0.4.1 – Stabilisierung

```text
Manifest URLs korrigieren
README/ARCHITECTURE/ROADMAP konsolidieren
diagnostics.py + Redaction
Reauthentication
HA-Level Tests
dynamische SmartFlex Entity Discovery
sensor.py modularisieren
services.py modularisieren
```

### v0.4.2 – Tarifvalidierung

```text
echte Fixed Fixture
echte Go Fixture
echte Heat Fixture
echte Dynamic Fixture
echte Intelligent Go 2024 Fixture
Intelligent EV Fixture
Intelligent Battery Fixture
DST Tests
SUPPORTED_TARIFFS aktualisieren
```

### v0.5 – Gas

```text
Gas Models
Gas Mapper
Gas Coordinator
Gas Entities
Tests
```

### v0.6 – Energy Dashboard

```text
Historical Consumption -> long-term statistics
Import / Export Trennung
Energy Dashboard Integration
```

### v0.7 – Advanced Tariffs

```text
Fan Club
SolarUp
PowerDrive
Zero Bills
PricingModifier/Capabilities bei Bedarf
```

### v0.8 – SmartFlex UX

```text
target_soc number entity
target_time time entity
dispatch binary sensor
next dispatch sensors
boost UX prüfen
capability-based entities
```

### v1.0

```text
stabile Fixture Matrix
vollständige HA Tests
stabile Unique IDs
Diagnostics
Reauth
HACS ready
Migration Guide
dokumentierte Support Matrix
```

---

# 32. Verbindlicher Arbeitsloop für Coding-Agenten

## Schritt 1 – Repository lesen

Vor Änderungen:

```bash
git status
git log --oneline -10
```

Danach relevante Dateien vollständig lesen. Nicht auf Basis alter Annahmen programmieren.

## Schritt 2 – Ziel bestimmen

Intern beantworten:

```text
Was ist das konkrete Problem?
Welche Schicht ist zuständig?
Welche bestehenden Models/APIs sind wiederverwendbar?
Welche Unique IDs dürfen nicht verändert werden?
Welche Tests sichern das aktuelle Verhalten?
```

## Schritt 3 – Schicht korrekt wählen

```text
GraphQL-Dictionary Interpretation -> API / Mapper
Tarifpreislogik                -> tariffs/
SmartFlex Fachlogik            -> capabilities/smartflex/
HA Darstellung                 -> entities/
```

## Schritt 4 – Tests zuerst oder parallel

Bei Bugfix:

```text
1. reproduzierenden Test schreiben
2. Test muss vorher fehlschlagen
3. Fix implementieren
4. Test muss danach bestehen
```

## Schritt 5 – Kleinster sinnvoller PR

Nicht gleichzeitig Refactoring + Feature + Entity-Rename + API-Rewrite + Doku-Cleanup mischen.

## Schritt 6 – Rückwärtskompatibilität

Prüfen:

```text
Unique IDs
Entity IDs
Config Entry
Device IDs
Services
Translations
Existing automations
```

## Schritt 7 – Tests/Lint

Mindestens:

```bash
pytest
ruff check .
```

Zusätzlich, wenn vorhanden:

```text
hassfest
HACS validation
```

## Schritt 8 – Dokumentation

Falls betroffen aktualisieren:

```text
README
ARCHITECTURE
ROADMAP
SUPPORTED_TARIFFS
RELEASE_NOTES
```

## Schritt 9 – Security Review

Prüfen:

```text
keine Tokens
keine Passwörter
keine Accounts
keine MALO/MELO
keine Meter IDs
keine Device IDs
keine vollständigen API Dumps
```

## Schritt 10 – Abschlussbericht

Jeder Agent berichtet:

```text
Changed:
- ...

Tests:
- ...

Compatibility:
- ...

Known limitations:
- ...

Follow-up:
- ...
```

---

# 33. Direkt nutzbarer Prompt für einen Coding-Agenten

```text
Arbeite am Repository https://github.com/thecem/octopus_energy_de.

Lies zuerst AGENT_WORK_INSTRUCTION.md vollständig und behandle die darin
definierten Architekturregeln als verbindlich.

Analysiere danach den aktuellen Stand des Repositories und implementiere die
angeforderte Änderung als möglichst kleinen, rückwärtskompatiblen Schritt.

Wichtige Regeln:

1. Keine Tariflogik anhand reiner Marketingnamen implementieren.
2. TariffType, ProductFamily und Capabilities getrennt halten.
3. SmartFlex ist eine Capability und kein Tariftyp.
4. Home-Assistant-Entities dürfen keine rohe GraphQL-Struktur auswerten.
5. GraphQL Parsing gehört in API/Mapper.
6. Tarifberechnung gehört in tariffs/.
7. SmartFlex-Domainlogik gehört in capabilities/smartflex/.
8. Keine festen 15/30/60-Minuten-Annahmen.
9. Keine hardcodierten Go-/Heat-Uhrzeiten, wenn Kraken Activation Rules liefert.
10. Unbekannte Tarife müssen sicher auf UNKNOWN fallen.
11. Bestehende Unique IDs und Config Entries nicht unnötig verändern.
12. Keine sensitiven Kraken-Daten loggen oder committen.
13. Für Änderungen Tests ergänzen.
14. Große Dateien weiter modularisieren statt zusätzliche Verantwortung dort
    einzubauen.
15. README, ARCHITECTURE, ROADMAP und SUPPORTED_TARIFFS bei Bedarf im selben
    PR aktualisieren.

Arbeitsablauf:

A. Aktuellen Code lesen.
B. Betroffene Architektur-Schicht bestimmen.
C. Tests für bestehendes/gewünschtes Verhalten definieren.
D. Kleinsten sinnvollen Patch implementieren.
E. Tests und Lint ausführen.
F. Rückwärtskompatibilität prüfen.
G. Security-/Privacy-Prüfung durchführen.
H. Dokumentation aktualisieren.
I. Abschließend Changed / Tests / Compatibility / Limitations / Follow-up
   berichten.

Wenn die reale Kraken-Struktur für einen Tarif unbekannt ist, nicht raten.
Stattdessen Fixture/Diagnostics anfordern oder UNKNOWN verwenden.

Bevor du einen neuen TariffType einführst, prüfe ausdrücklich, ob das Produkt
nicht besser als Kombination aus bestehendem Pricing Model + Product Family +
Capabilities/Modifiers modelliert werden kann.
```

---

# 34. Prompt für autonomen Agent-Loop

```text
Führe folgenden Loop aus, bis das definierte Issue vollständig erfüllt ist:

1. Lies AGENT_WORK_INSTRUCTION.md.
2. Prüfe git status und letzte Commits.
3. Lies nur die für den aktuellen Schritt relevanten Dateien.
4. Wähle genau einen kleinen Teil des Issues.
5. Schreibe oder aktualisiere Tests.
6. Implementiere den kleinsten Patch.
7. Führe Tests/Lint aus.
8. Falls Tests fehlschlagen:
   - Ursache analysieren
   - keine Tests löschen, um grün zu werden
   - Implementierung korrigieren
9. Prüfe Architecture Rules.
10. Prüfe Unique IDs und Kompatibilität.
11. Prüfe Privacy/Security.
12. Aktualisiere Dokumentation.
13. Committe logisch zusammengehörige Änderungen.
14. Fahre mit dem nächsten kleinen Teil fort.

Stoppe und dokumentiere einen Blocker, wenn:
- reale Kraken-Daten fehlen,
- API-Struktur unbekannt ist,
- eine Änderung einen Breaking Change erfordern würde,
- eine Unique-ID-Migration nötig wäre.

In diesen Fällen nicht raten und keinen erfundenen API-Code implementieren.
```

---

# 35. Definition of Done

Eine Aufgabe ist nur fertig, wenn:

```text
[ ] Architekturregeln eingehalten
[ ] keine unnötige neue Monolith-Logik
[ ] Tests vorhanden
[ ] Tests grün
[ ] Lint grün
[ ] keine sensitiven Daten
[ ] Unknown-Fallback berücksichtigt
[ ] Unique IDs geprüft
[ ] Dokumentation geprüft
[ ] SUPPORTED_TARIFFS bei Tarifänderungen aktualisiert
[ ] Release Notes bei Nutzeränderungen aktualisiert
```

---

# 36. Ausdrücklich nicht tun

```text
- neuen Tarif nur anhand Name hardcoden
- Go/Heat Zeiten ohne API-Notwendigkeit hardcoden
- SmartFlex als TariffType modellieren
- GraphQL-Dictionaries direkt in sensor.py parsen
- API Calls in Entity-Schleifen machen
- komplette API Responses loggen
- echte Kundendaten als Fixture committen
- unbekannte Produkte mit Exception abbrechen
- große Features direkt in sensor.py/services.py schreiben
- Tests entfernen, damit CI grün wird
- Unique IDs ohne Migration ändern
```

---

# 37. Leitgedanke

Wenn Octopus eine neue Produktgeneration veröffentlicht, soll möglichst Folgendes reichen:

```text
neue API-Daten
    |
    v
Mapper erkennt vorhandenes Pricing Model
    |
    v
Product Family / Capabilities werden ergänzt
    |
    v
bestehende generische Handler funktionieren weiter
```

Nicht:

```text
neuer Produktname
    |
    v
neue Spezialklasse
    |
    v
hardcodierte Zeitlogik
    |
    v
weitere Sonderfälle in sensor.py
```

Das ist die zentrale Qualitätsregel dieses Projekts.

# v0.4.1 - Stabilization

## Included

- Corrected manifest documentation and issue-tracker URLs.
- Reauthentication flow for updated Octopus credentials.
- Automated fixture privacy check for authentication, account, meter, and device markers.

# v0.4.0 - SmartFlex control

## Included

- Smart Control switches that suspend or resume eligible SmartFlex devices.
- Boost Charge switches that start or cancel a Boost session.
- `octopus_energy_de.set_device_preferences` service with validated target state of charge and target time.
- Independent polling intervals: 30 minutes for tariffs, 60 minutes for meters, and 3 minutes for SmartFlex.
- `octopus_energy_de.get_electricity_consumption` service for on-demand historical interval data.
- `octopus_energy_de.export_electricity_consumption_csv` service for CSV exports of up to 31 days, with a configurable directory below `config/www` and a download notification.

## Safety

- All SmartFlex actions require an explicit switch or service invocation.
- The integration does not issue control mutations during polling or setup.

# v0.3.0 - SmartFlex foundation

## Included

- Electricity meters and newest available readings for every returned OBIS register.
- Previous-day electricity consumption with Kraken interval boundaries preserved.
- Read-only SmartFlex devices, completed dispatches, and charging sessions.
- SmartFlex device state, state of charge, and charging-power sensors when available.

## Not included

- Smart Control, Boost, or device preference changes. These remain planned for v0.4.0.
- Gas support, planned for v0.5.0.

# v0.1.0 - Initial development release

This is the first clean-room architecture release of **Octopus Energy DE** for Home Assistant.

## Included

- New Home Assistant domain: `octopus_energy_de`
- UI config flow with Octopus Germany email/password authentication
- Multiple-account selection
- German Kraken GraphQL transport using Home Assistant's aiohttp stack
- Modular tariff domain separated from API and Home Assistant entities
- Technical tariff types: Fixed, Time of Use, Dynamic, Unknown
- Marketing families kept separate from pricing behavior
- Initial family recognition for Octopus Go, Octopus Heat, dynamicOctopus, Intelligent Octopus and legacy Intelligent Octopus Go
- Electricity entities per supply point:
  - Current rate
  - Next rate
  - Tariff
- Data-driven dynamic intervals (no fixed 15/30/60 minute assumption)
- Time-of-use rules read from Kraken activation rules (no hardcoded Go/Heat hours)
- Anonymized tariff fixture export tool
- Dev Container, pytest/ruff workflow and GitHub Actions
- HACS repository metadata

## Not included yet

- SmartFlex device control / Intelligent dispatches
- EV state of charge and charging sessions
- Gas
- Consumption / historical meter data
- Services/actions such as Boost
- Migration of entity IDs from `octopus_germany`

The existing `octopus_germany` integration can remain installed while this release is tested because the Home Assistant domain is different.

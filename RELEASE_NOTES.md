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

# Octopus Energy DE for Home Assistant

A new, modular Home Assistant custom integration for the **German Octopus Energy Kraken API**.

> **Status: v0.4.1 development release.** Installable next to the older `octopus_germany` integration because this project uses the distinct Home Assistant domain `octopus_energy_de`.

This project is unofficial and is not affiliated with Octopus Energy.

## Why a new integration?

The project starts with a clean architecture instead of migrating a large legacy module in place. The design separates:

```text
Kraken GraphQL
      |
      v
api / transport / auth
      |
      v
mappers -> normalized models
      |
      v
tariffs / capabilities
      |
      v
coordinators
      |
      v
Home Assistant entities
```

Marketing product names are deliberately separated from technical tariff behavior. `Octopus Go` and `Octopus Heat`, for example, can both use the generic Time-of-Use handler while their product families remain distinguishable.

## v0.4.1 features

  - Fixed
  - Time of Use
  - Dynamic
  - Unknown fallback
  - Octopus Go
  - Octopus Heat
  - dynamicOctopus
  - Intelligent Octopus
  - legacy Intelligent Octopus Go
  - Current rate (`EUR/kWh`)
  - Next rate (`EUR/kWh`)
  - Tariff information
      - Latest electricity meter reading for every returned OBIS register
      - Previous-day electricity consumption with Kraken interval boundaries preserved
      - Read-only SmartFlex device state, state of charge, charging power, dispatches, and charging sessions
      - Smart Control and Boost Charge switches for eligible SmartFlex devices
      - `octopus_energy_de.set_device_preferences` service for target state of charge and time
      - Reauthentication when Octopus credentials change

See [RELEASE_NOTES.md](RELEASE_NOTES.md) and [ROADMAP.md](ROADMAP.md).

## Polling

- Tariff and supply data: every 30 minutes.
- Electricity meter readings: every 60 minutes.
- SmartFlex device and dispatch data: every 3 minutes.
- Historical consumption: only through `octopus_energy_de.get_electricity_consumption` for a requested date.

## Consumption Export

Export a selected period as CSV with `octopus_energy_de.export_electricity_consumption_csv`:

```yaml
start_date: "2026-09-01"
end_date: "2026-09-03"
# Optional: restrict to one supply point.
# supply_point_id: "..."
# Optional: subdirectory below config/www.
# directory: "octopus_energy_de_exports"
```

The export is limited to 31 days, is written by default to `config/www/octopus_energy_de_exports/`, and creates a persistent notification with a download link.

## Parallel installation with `octopus_germany`

The two integrations have different Home Assistant domains:

```text
old: custom_components/octopus_germany/
new: custom_components/octopus_energy_de/
```

Home Assistant therefore treats them as separate integrations. During development you can keep the existing integration active and add **Octopus Energy DE** to compare the price sensors.

Do not expect identical entity IDs: v0.1.0 intentionally creates a separate test surface.

## Manual installation

Copy:

```text
custom_components/octopus_energy_de
```

into your Home Assistant configuration:

```text
/config/custom_components/octopus_energy_de
```

Restart Home Assistant, then open:

```text
Settings -> Devices & services -> Add integration -> Octopus Energy DE
```

Enter your Octopus Energy Germany login credentials and choose an account if the login has multiple accounts.

## HACS during development

1. Push this repository to GitHub.
2. Replace `YOUR_GITHUB_USER` in `manifest.json` with the repository owner.
3. Create the GitHub release `v0.1.0`.
4. Add the repository to HACS as a custom **Integration** repository.
5. Download and restart Home Assistant.

The repository contains `hacs.json` and a HACS validation workflow.

## Dev Container

Requirements on the host:


Open the repository and choose **Reopen in Container**.

The container uses Python 3.14, installs Home Assistant and the development dependencies, forwards port `8123`, and links the integration into the local HA test configuration.

Then run:

```bash
scripts/develop
```

Open:

```text
http://localhost:8123
```

Run tests:

```bash
scripts/test
```

Run lint/compile checks:

```bash
scripts/lint
```

The local HA configuration is stored under `config/` and is ignored by Git except for `.gitkeep`.

## Collecting real tariff fixtures

The next important development step is collecting **real, anonymized German Kraken tariff structures**.

Inside the Dev Container:

```bash
export OCTOPUS_EMAIL='your-login@example.com'
export OCTOPUS_PASSWORD='your-password'
python scripts/export_tariff_fixture.py tests/fixtures/my_tariff.json
```

For a specific account:

```bash
python scripts/export_tariff_fixture.py tests/fixtures/my_tariff.json --account YOUR_ACCOUNT_NUMBER
```

Credentials, account numbers, MALO/MELO numbers, meter IDs, property IDs and device IDs are **not written into the fixture**. The exporter only retains agreement/product/rate data needed to understand tariff behavior.

Always inspect a fixture manually before committing it.

## Tariff architecture

Technical type:

```text
FIXED
TIME_OF_USE
DYNAMIC
UNKNOWN
```

Product family:

```text
GENERIC_FIXED
OCTOPUS_GO
OCTOPUS_HEAT
DYNAMIC_OCTOPUS
INTELLIGENT_OCTOPUS
INTELLIGENT_OCTOPUS_GO_LEGACY
UNKNOWN
```

Those two dimensions must remain separate.

A future SmartFlex-enabled dynamic account should therefore be representable as conceptually:

```text
Tariff type: DYNAMIC
Product family: DYNAMIC_OCTOPUS
Capabilities: SMARTFLEX + EV
```

SmartFlex will be added as a capability layer rather than as another tariff algorithm.

## Important v0.1.0 limitations

This is an early test release. It intentionally does not yet include:


The first priority is to validate the German tariff API structures using anonymized real fixtures.

## API provenance

The German Kraken endpoint and the GraphQL fields used in this release were cross-checked against the existing `thecem/octopus_germany` integration. The modular architecture is influenced by the separation of domains in `BottlecapDave/HomeAssistant-OctopusEnergy`, but this repository implements the German API directly and does not port the UK API.

Useful references:


## Security


## License

MIT. See [LICENSE](LICENSE).

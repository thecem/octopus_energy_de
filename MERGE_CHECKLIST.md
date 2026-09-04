# Before merging this metadata pack

This pack targets `octopus_energy_de` and is intended as a metadata/branding
overlay for the current repository.

## 1. Version

The supplied `manifest.json` uses:

```json
"version": "0.4.1"
```

Change it if the target release has a different version.

## 2. Service names

The supplied `services.yaml` documents the currently known/recommended actions:

- `set_device_preferences`
- `get_consumption`
- `export_consumption_csv`

Before merging, compare these names and fields with the actual calls to
`hass.services.async_register(...)` or equivalent in the current source tree.

If implementation names differ, the Python implementation is authoritative:
update `services.yaml` to match it exactly.

## 3. Reauthentication strings

`strings.json` and `translations/de.json` include `reauth_confirm` text in
preparation for native Home Assistant reauthentication.

If reauthentication has not yet been implemented in `config_flow.py`, keeping
the strings is harmless, but the feature should not be documented as available
until `async_step_reauth` / `async_step_reauth_confirm` exist.

## 4. Brand files

Run:

```bash
python -m pip install pillow
python scripts/fetch_brand_assets.py
```

Commit the four generated PNG files. The validation workflow intentionally
fails if `icon.png` or `logo.png` is missing.

## 5. GitHub repository settings

For HACS discoverability, ensure the GitHub repository has:

- a short repository description
- Issues enabled
- topics such as:
  `home-assistant`, `hacs`, `octopus-energy`, `energy`, `germany`,
  `smartflex`, `home-assistant-integration`

## 6. HACS default store

Local brand assets work in Home Assistant 2026.3+, but HACS default-store
submission may still check `home-assistant/brands`. If submitting to the HACS
default repository, follow the current HACS checklist and its brands check.

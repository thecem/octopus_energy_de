# Contributing

## Development rules

1. Keep Kraken GraphQL transport separate from tariff and Home Assistant entity logic.
2. Do not introduce pricing branches based only on product-code equality.
3. Do not hardcode Go or Heat clock times if Kraken provides activation rules.
4. Do not assume dynamic interval lengths.
5. Add an anonymized fixture before declaring a new German product family supported.
6. Do not commit account numbers, MALO/MELO identifiers, meter/device IDs, addresses, credentials or tokens.
7. Keep changes small enough to review and accompany behavior changes with tests.

## Local workflow

```bash
scripts/setup
scripts/test
scripts/lint
scripts/develop
```

## Release workflow

- Update `VERSION` in `const.py` and `version` in `manifest.json` together.
- Update `RELEASE_NOTES.md`.
- Tag the release as `vX.Y.Z`.
- Publishing a GitHub Release triggers `.github/workflows/release.yml`, which creates `octopus_energy_de.zip` containing only the integration directory.

# Validation report for v0.1.0 package

Validated in the build environment:

- `python -m compileall -q custom_components tests` -> passed
- `pytest -q` -> 5 passed

Ruff is configured in `pyproject.toml` and installed by the Dev Container through `requirements-dev.txt`. It could not be executed in the artifact build environment because that environment has no package-network access. Run `scripts/lint` once inside the Dev Container before publishing the GitHub release.

Live Kraken authentication was not executed while building this archive because no user credentials were provided to the build environment. The endpoint, authentication mutation and tariff query fields were cross-checked against the current `thecem/octopus_germany` source before packaging.

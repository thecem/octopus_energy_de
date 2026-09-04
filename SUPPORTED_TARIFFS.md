# German tariff validation matrix

`SUPPORTED` requires a real anonymized Kraken fixture plus tests. Marketing visibility alone is not enough.

| Product family | Technical type | Real fixture | v0.1.0 status | Notes |
|---|---|---:|---|---|
| Generic fixed | FIXED | No | CODE_READY | Needs real DE fixture |
| Octopus Go | TIME_OF_USE | No | CODE_READY | Times read from Kraken rules |
| Octopus Heat | TIME_OF_USE | No | CODE_READY | Generic TOU handler |
| dynamicOctopus | DYNAMIC | No | CODE_READY | Forecast intervals are data-driven |
| Intelligent Octopus Go 2024 | expected TIME_OF_USE | No | DISCOVERED | Legacy fixture is a priority |
| Intelligent Octopus | API must confirm | No | DISCOVERED | SmartFlex is not a tariff type |
| PowerDrive | Unknown | No | DISCOVERED | Do not classify without API data |
| SolarUp | Unknown | No | DISCOVERED | Do not classify without API data |
| Fan Club | Unknown | No | DISCOVERED | Do not classify without API data |
| Zero Bills | Unknown | No | DISCOVERED | Do not classify without API data |

## Status definitions

- `SUPPORTED`: real fixture and automated tests exist.
- `CODE_READY`: generic code path exists, but no real fixture is committed yet.
- `DISCOVERED`: known product, technical Kraken structure not yet verified.
- `LEGACY_SUPPORTED`: legacy product backed by a real fixture and tests.

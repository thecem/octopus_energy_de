# Architecture

## Layering

```text
Home Assistant
      sensor.py / switch.py / services.py
      |
      v
coordinator.py
      |
      v
TariffService ---------------- future Capability services
      |                              |
      v                              v
tariffs/                         capabilities/
      ^                              ^
      |                              |
normalized models <------------- mappers
      ^                              ^
      |                              |
api/client.py -> api/graphql -> Kraken GraphQL
```

## Invariants

### API layer

Knows GraphQL field names and authentication. It does not calculate Home Assistant entity states.

### Mapper layer

Converts Kraken dictionaries into typed internal models. GraphQL naming must not leak into entities.

### Tariff layer

Contains technical price behavior. It is selected by technical structure, not solely by product marketing names.

### Capability layer

Future SmartFlex, vehicle, battery and heat-pump features belong here. `Intelligent` must not become a technical pricing type.

### Entity layer

Should remain thin: read coordinator models and expose Home Assistant state/attributes.

## Polling

Base tariff and supply data, meter readings, and SmartFlex data use separate coordinators. Historical consumption is loaded only through on-demand services.

## v0.1.0 technical compromises

TOU rules are represented as recurring local-time windows instead of pre-expanded absolute intervals. This is intentionally isolated behind `TimeOfUseTariffHandler`. Real German fixtures will determine whether future versions should expand rules into timezone-aware absolute intervals for stronger DST handling.

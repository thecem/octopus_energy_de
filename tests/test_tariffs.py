import json
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from custom_components.octopus_energy_de.api.mappers.tariff import map_tariff
from custom_components.octopus_energy_de.tariffs.registry import TariffService
from custom_components.octopus_energy_de.tariffs.types import TariffFamily, TariffType

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mein_tarif.json"


def test_fixed_mapping_and_rate():
    agreement = {
        "product": {"code": "FIXED-TEST", "fullName": "Fixed Test", "isTimeOfUse": False},
        "unitRateInformation": {
            "__typename": "SimpleProductUnitRateInformation",
            "latestGrossUnitRateCentsPerKwh": 30.5,
        },
        "unitRateForecast": [],
        "validFrom": "2026-01-01T00:00:00Z",
        "validTo": "2027-01-01T00:00:00Z",
    }
    tariff = map_tariff(agreement)
    assert tariff.tariff_type is TariffType.FIXED
    assert TariffService.current_rate(tariff, datetime.now(UTC)) == Decimal("0.305")


def test_dynamic_interval_length_is_data_driven():
    agreement = {
        "product": {"code": "DYNAMIC-TEST", "fullName": "dynamicOctopus", "isTimeOfUse": False},
        "unitRateInformation": {"__typename": "SimpleProductUnitRateInformation"},
        "unitRateForecast": [
            {
                "validFrom": "2026-09-04T10:00:00Z",
                "validTo": "2026-09-04T10:10:00Z",
                "unitRateInformation": {
                    "__typename": "SimpleProductUnitRateInformation",
                    "latestGrossUnitRateCentsPerKwh": 21,
                },
            },
            {
                "validFrom": "2026-09-04T10:10:00Z",
                "validTo": "2026-09-04T10:40:00Z",
                "unitRateInformation": {
                    "__typename": "SimpleProductUnitRateInformation",
                    "latestGrossUnitRateCentsPerKwh": 18,
                },
            },
        ],
        "validFrom": "2026-01-01T00:00:00Z",
        "validTo": None,
    }
    tariff = map_tariff(agreement)
    assert tariff.tariff_type is TariffType.DYNAMIC
    assert tariff.family is TariffFamily.DYNAMIC_OCTOPUS
    now = datetime(2026, 9, 4, 10, 25, tzinfo=UTC)
    assert TariffService.current_rate(tariff, now) == Decimal("0.18")


def test_go_and_heat_are_both_time_of_use():
    for code, name, family in [
        ("OCTOPUS-GO", "Octopus Go", TariffFamily.OCTOPUS_GO),
        ("OCTOPUS-HEAT", "Octopus Heat", TariffFamily.OCTOPUS_HEAT),
    ]:
        agreement = {
            "product": {"code": code, "fullName": name, "isTimeOfUse": True},
            "unitRateInformation": {
                "__typename": "TimeOfUseProductUnitRateInformation",
                "rates": [
                    {
                        "latestGrossUnitRateCentsPerKwh": 20,
                        "timeslotName": "LOW",
                        "timeslotActivationRules": [
                            {"activeFromTime": "00:00:00", "activeToTime": "05:00:00"}
                        ],
                    },
                    {
                        "latestGrossUnitRateCentsPerKwh": 30,
                        "timeslotName": "STANDARD",
                        "timeslotActivationRules": [
                            {"activeFromTime": "05:00:00", "activeToTime": "00:00:00"}
                        ],
                    },
                ],
            },
            "unitRateForecast": [],
        }
        tariff = map_tariff(agreement)
        assert tariff.tariff_type is TariffType.TIME_OF_USE
        assert tariff.family is family


def test_real_intelligent_go_fixture_distinguishes_fixed_and_tou_tariffs():
    agreements = json.loads(FIXTURE_PATH.read_text())["agreements"]
    tariffs = {agreement["product"]["code"]: map_tariff(agreement) for agreement in agreements}

    go_light = tariffs["DEU-ELECTRICITY-IO-GO-LIGHT-24"]
    assert go_light.tariff_type is TariffType.FIXED
    assert go_light.fixed_rate_eur_per_kwh == Decimal("0.237762")

    intelligent_go = tariffs["DEU-ELECTRICITY-IO-GO-24"]
    assert intelligent_go.tariff_type is TariffType.TIME_OF_USE
    assert intelligent_go.family is TariffFamily.INTELLIGENT_OCTOPUS_GO_LEGACY
    assert [(rate.name, rate.value_eur_per_kwh) for rate in intelligent_go.tou_rates] == [
        ("GO", Decimal("0.150654")),
        ("STANDARD", Decimal("0.282744")),
    ]

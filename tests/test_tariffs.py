from datetime import datetime, timezone
from decimal import Decimal

from custom_components.octopus_energy_de.api.mappers.tariff import map_tariff
from custom_components.octopus_energy_de.tariffs.registry import TariffService
from custom_components.octopus_energy_de.tariffs.types import TariffFamily, TariffType


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
    assert TariffService.current_rate(tariff, datetime.now(timezone.utc)) == Decimal("0.305")


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
    now = datetime(2026, 9, 4, 10, 25, tzinfo=timezone.utc)
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

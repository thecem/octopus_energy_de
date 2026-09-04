from datetime import date, timedelta
from typing import Any

from custom_components.octopus_energy_de.api.mappers.account import map_account_snapshot
from custom_components.octopus_energy_de.api.mappers.consumption import (
    map_electricity_consumption,
)
from custom_components.octopus_energy_de.api.mappers.meter import (
    map_electricity_meter_readings,
    map_latest_electricity_meter_reading,
)


def test_account_snapshot_maps_electricity_meters():
    response: dict[str, Any] = {
        "data": {
            "account": {
                "allProperties": [
                    {
                        "id": "property-id",
                        "electricityMalos": [
                            {
                                "maloNumber": "malo-id",
                                "meters": [
                                    {"id": "meter-id", "number": "123456",
                                        "meterType": "SMART"}
                                ],
                                "agreements": [
                                    {
                                        "product": {"code": "FIXED", "fullName": "Fixed"},
                                        "unitRateInformation": {
                                            "__typename": "SimpleProductUnitRateInformation"
                                        },
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        }
    }

    snapshot = map_account_snapshot("account", response)

    assert snapshot.electricity[0].meters[0].meter_id == "meter-id"
    assert snapshot.electricity[0].meters[0].number == "123456"
    assert snapshot.electricity[0].meters[0].meter_type == "SMART"


def test_latest_electricity_meter_reading_preserves_api_value_and_timestamp():
    response: dict[str, Any] = {
        "data": {
            "electricityMeterReadings": {
                "edges": [
                    {
                        "node": {
                            "value": "1234.567",
                            "readAt": "2026-09-03T12:00:00Z",
                            "registerObisCode": "1-0:1.8.0",
                            "registerType": "IMPORT",
                        }
                    }
                ]
            }
        }
    }

    reading = map_latest_electricity_meter_reading("meter-id", response)

    assert reading is not None
    assert str(reading.value) == "1234.567"
    assert reading.read_at is not None
    assert reading.register_obis_code == "1-0:1.8.0"


def test_meter_mapping_keeps_the_newest_reading_for_each_obis_register():
    response: dict[str, Any] = {
        "data": {
            "electricityMeterReadings": {
                "edges": [
                    {
                        "node": {
                            "value": "100",
                            "readAt": "2026-09-01T00:00:00Z",
                            "registerObisCode": "1-0:1.8.0",
                        }
                    },
                    {
                        "node": {
                            "value": "110",
                            "readAt": "2026-09-02T00:00:00Z",
                            "registerObisCode": "1-0:1.8.0",
                        }
                    },
                    {
                        "node": {
                            "value": "40",
                            "readAt": "2026-09-02T00:00:00Z",
                            "registerObisCode": "1-0:1.8.1",
                        }
                    },
                ]
            }
        }
    }

    readings = map_electricity_meter_readings("meter-id", response)

    assert {(reading.register_obis_code, str(reading.value)) for reading in readings} == {
        ("1-0:1.8.0", "110"),
        ("1-0:1.8.1", "40"),
    }


def test_consumption_mapping_preserves_each_api_interval():
    response: dict[str, Any] = {
        "data": {
            "account": {
                "property": {
                    "measurements": {
                        "edges": [
                            {
                                "node": {
                                    "startAt": "2026-09-03T00:00:00Z",
                                    "endAt": "2026-09-03T00:15:00Z",
                                    "value": "0.42",
                                    "unit": "kwh",
                                }
                            },
                            {
                                "node": {
                                    "startAt": "2026-09-03T00:15:00Z",
                                    "endAt": "2026-09-03T00:45:00Z",
                                    "value": "0.84",
                                    "unit": "kwh",
                                }
                            },
                        ]
                    }
                }
            }
        }
    }

    consumption = map_electricity_consumption(
        "property-id", date(2026, 9, 3), response)

    assert [interval.end - interval.start for interval in consumption.intervals] == [
        timedelta(minutes=15),
        timedelta(minutes=30),
    ]
    assert [str(interval.value)
            for interval in consumption.intervals] == ["0.42", "0.84"]

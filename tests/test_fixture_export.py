import importlib.util
import json
from pathlib import Path


EXPORTER_PATH = Path(__file__).parents[1] / \
    "scripts" / "export_tariff_fixture.py"
TARIFF_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "mein_tarif.json"
SPEC = importlib.util.spec_from_file_location(
    "export_tariff_fixture", EXPORTER_PATH)
assert SPEC and SPEC.loader
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)


def test_measurement_export_omits_values_identifiers_and_absolute_timestamps():
    response = {
        "data": {
            "account": {
                "property": {
                    "measurements": {
                        "edges": [
                            {
                                "node": {
                                    "startAt": "2026-09-03T00:00:00Z",
                                    "endAt": "2026-09-03T00:15:00Z",
                                    "unit": "KWH",
                                    "value": "0.42",
                                    "meterId": "private-meter-id",
                                }
                            }
                        ]
                    }
                }
            }
        }
    }

    assert exporter.minimize_measurements(response) == [
        {
            "start_offset_seconds": 0,
            "end_offset_seconds": 900,
            "unit": "KWH",
        }
    ]


def test_real_measurement_fixture_contains_full_day_of_quarter_hour_intervals():
    fixture = json.loads(TARIFF_FIXTURE_PATH.read_text())
    intervals = fixture["electricity_measurement_intervals"]

    assert len(intervals) == 96
    assert {
        interval["end_offset_seconds"] - interval["start_offset_seconds"]
        for interval in intervals
    } == {900}
    assert {interval["unit"] for interval in intervals} == {"kwh"}

from decimal import Decimal

from custom_components.octopus_energy_de.api.mappers.smartflex import map_smartflex_snapshot


def test_smartflex_mapping_includes_device_dispatch_and_charging_session():
    response = {
        "data": {
            "completedDispatches": [
                {"start": "2026-09-04T00:00:00Z", "end": "2026-09-04T01:00:00Z", "deltaKwh": "7.2"}
            ],
            "devices": [
                {
                    "id": "device-id",
                    "name": "EV",
                    "deviceType": "ELECTRIC_VEHICLES",
                    "provider": "Provider",
                    "status": {"currentState": "CHARGING", "stateOfCharge": {"value": "72"}},
                    "vehicleVariant": {"batterySize": "60"},
                    "chargingSessions": {
                        "edges": [
                            {
                                "node": {
                                    "start": "2026-09-04T00:00:00Z",
                                    "end": "2026-09-04T01:00:00Z",
                                    "energyAdded": {"value": "7.2"},
                                    "cost": {"amount": "0.9"},
                                    "type": "SMART",
                                }
                            }
                        ]
                    },
                }
            ],
        }
    }

    snapshot = map_smartflex_snapshot(response)

    assert snapshot.devices[0].state_of_charge == Decimal("72")
    assert snapshot.devices[0].battery_size_kwh == Decimal("60")
    assert snapshot.dispatches[0].energy_kwh == Decimal("7.2")
    assert snapshot.charging_sessions[0].cost_eur == Decimal("0.9")

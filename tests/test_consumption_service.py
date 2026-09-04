import asyncio
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

from custom_components.octopus_energy_de.actions.consumption import (
    async_get_electricity_consumption,
)
from custom_components.octopus_energy_de.actions.export import write_consumption_csv
from custom_components.octopus_energy_de.api.models.tariff import (
    ElectricityConsumption,
    ElectricityConsumptionInterval,
    ElectricitySupply,
    Tariff,
)
from custom_components.octopus_energy_de.tariffs.types import TariffType


def test_consumption_service_fetches_only_the_requested_day():
    interval = ElectricityConsumptionInterval(
        start=datetime(2026, 9, 3, tzinfo=UTC),
        end=datetime(2026, 9, 3, 0, 15, tzinfo=UTC),
        value=Decimal("0.42"),
        unit="kwh",
    )
    supply = ElectricitySupply(
        supply_point_id="supply", property_id="property", tariff=Tariff("code", "name", TariffType.FIXED)
    )

    class Client:
        async def electricity_consumption(self, account, property_id, measurement_date):
            assert (account, property_id, measurement_date) == (
                "account", "property", date(2026, 9, 3))
            return ElectricityConsumption("property", measurement_date, (interval,))

    runtime = SimpleNamespace(
        client=Client(),
        coordinator=SimpleNamespace(
            account_number="account", data=SimpleNamespace(electricity=(supply,))),
    )
    hass = SimpleNamespace(config_entries=SimpleNamespace(
        async_entries=lambda domain: [SimpleNamespace(runtime_data=runtime)]))
    call = SimpleNamespace(data={"date": "2026-09-03"})

    result = asyncio.run(async_get_electricity_consumption(hass, call))

    assert result["consumption"][0]["total_kwh"] == "0.42"


def test_consumption_csv_contains_one_row_per_interval(tmp_path: Path):
    output_path = tmp_path / "consumption.csv"

    write_consumption_csv(
        output_path,
        {"measurement_scope": "property", "supply_point_id": "supply"},
        [{"date": "2026-09-03", "start": "a", "end": "b", "consumption_kwh": "0.42"}],
    )

    assert output_path.read_text(
    ) == "# measurement_scope=property\n# supply_point_id=supply\ndate,start,end,consumption_kwh\n2026-09-03,a,b,0.42\n"

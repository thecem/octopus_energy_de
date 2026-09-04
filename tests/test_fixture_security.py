from pathlib import Path

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
FORBIDDEN_MARKERS = (
    "@example.com",
    "authorization",
    "bearer",
    "token",
    "accountnumber",
    "malo",
    "melo",
    "meterserial",
    "streetaddress",
    "postalcode",
    "password",
    "deviceid",
    "propertyid",
)


def test_json_fixtures_do_not_contain_sensitive_markers():
    for fixture_path in FIXTURE_DIRECTORY.glob("*.json"):
        content = fixture_path.read_text(encoding="utf-8").lower()
        assert not any(
            marker in content for marker in FORBIDDEN_MARKERS), fixture_path

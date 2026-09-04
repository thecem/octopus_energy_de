from custom_components.octopus_energy_de.tariffs.families import detect_family
from custom_components.octopus_energy_de.tariffs.types import TariffFamily


def test_legacy_intelligent_go_has_specific_family():
    assert detect_family("INTELLIGENT-OCTOPUS-GO-2024", "Intelligent Octopus Go") is TariffFamily.INTELLIGENT_OCTOPUS_GO_LEGACY


def test_unknown_product_is_safe():
    assert detect_family("FUTURE-PRODUCT-2099", "Future") is TariffFamily.UNKNOWN

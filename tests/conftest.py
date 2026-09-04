"""Allow domain modules to be tested without importing Home Assistant integration bootstrap."""

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

custom_components = types.ModuleType("custom_components")
custom_components.__path__ = [str(ROOT / "custom_components")]
sys.modules.setdefault("custom_components", custom_components)

integration = types.ModuleType("custom_components.octopus_energy_de")
integration.__path__ = [str(ROOT / "custom_components" / "octopus_energy_de")]
sys.modules.setdefault("custom_components.octopus_energy_de", integration)

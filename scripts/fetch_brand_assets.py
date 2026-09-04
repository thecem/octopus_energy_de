#!/usr/bin/env python3
"""Fetch official Octopus Energy DE press logos and build Home Assistant brand assets.

Source:
https://octopusenergy.de/newsroom/pressebilder

The press page explicitly provides these Octopus Energy logos for download.
This script preserves the official artwork and only performs proportional
resizing and transparent padding.

Requires:
    python -m pip install pillow
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "custom_components" / "octopus_energy_de" / "brand"

STACKED_URL = "https://a.storyblok.com/f/144190/826x366/e9d231e064/stacked-logo.png"
DEFAULT_URL = "https://a.storyblok.com/f/144190/1293x200/461e2508f6/default-logo.png"

USER_AGENT = "octopus-energy-de-home-assistant-brand-fetch/1.0"


def download(url: str) -> Image.Image:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return Image.open(BytesIO(response.read())).convert("RGBA")


def transparent_square(image: Image.Image, size: int) -> Image.Image:
    # Keep the official artwork unchanged; only scale proportionally and pad.
    inner = int(size * 0.88)
    fitted = ImageOps.contain(image, (inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - fitted.width) // 2
    y = (size - fitted.height) // 2
    canvas.alpha_composite(fitted, (x, y))
    return canvas


def proportional_logo(image: Image.Image, width: int) -> Image.Image:
    ratio = width / image.width
    height = max(1, round(image.height * ratio))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", optimize=True)


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)

    stacked = download(STACKED_URL)
    default = download(DEFAULT_URL)

    save_png(transparent_square(stacked, 256), BRAND / "icon.png")
    save_png(transparent_square(stacked, 512), BRAND / "icon@2x.png")
    save_png(proportional_logo(default, 512), BRAND / "logo.png")
    save_png(proportional_logo(default, 1024), BRAND / "logo@2x.png")

    print("Created:")
    for name in ("icon.png", "icon@2x.png", "logo.png", "logo@2x.png"):
        print(f"  {BRAND / name}")


if __name__ == "__main__":
    main()

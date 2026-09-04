#!/usr/bin/env python3
"""Build Home Assistant brand assets from official Octopus Energy Germany logos.

Official source:
https://octopusenergy.de/newsroom/pressebilder

The press page offers the Octopus Energy logos for download. The Home Assistant
icon is extracted from the official stacked logo by selecting the largest
connected non-transparent component (the octopus signet) and placing it,
unchanged, on a transparent square canvas.

The full horizontal logo is preserved for logo.png/logo@2x.png.

Requires:
    python -m pip install pillow
"""

from __future__ import annotations

from collections import deque
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "custom_components" / "octopus_energy_de" / "brand"

PRESS_PAGE = "https://octopusenergy.de/newsroom/pressebilder"
STACKED_URL = "https://a.storyblok.com/f/144190/826x366/e9d231e064/stacked-logo.png"
DEFAULT_URL = "https://a.storyblok.com/f/144190/1293x200/461e2508f6/default-logo.png"

USER_AGENT = "octopus-energy-de-home-assistant-brand-fetch/1.1"


def download(url: str) -> Image.Image:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        return Image.open(BytesIO(response.read())).convert("RGBA")


def _alpha_mask(image: Image.Image, threshold: int = 16) -> list[list[bool]]:
    alpha = image.getchannel("A")
    w, h = image.size
    px = alpha.load()
    return [[px[x, y] > threshold for x in range(w)] for y in range(h)]


def largest_connected_component_bbox(
    image: Image.Image,
    threshold: int = 16,
) -> tuple[int, int, int, int]:
    """Return bounding box of the largest connected alpha component.

    This is designed for the official stacked Octopus Energy artwork:
    the octopus signet is a single large connected shape, while the
    wordmark is split into many smaller letter components.
    """

    mask = _alpha_mask(image, threshold)
    w, h = image.size
    visited = bytearray(w * h)

    best_count = 0
    best_bbox: tuple[int, int, int, int] | None = None

    def idx(x: int, y: int) -> int:
        return y * w + x

    for y in range(h):
        for x in range(w):
            if not mask[y][x] or visited[idx(x, y)]:
                continue

            queue = deque([(x, y)])
            visited[idx(x, y)] = 1

            count = 0
            min_x = max_x = x
            min_y = max_y = y

            while queue:
                cx, cy = queue.popleft()
                count += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in (
                    (cx - 1, cy),
                    (cx + 1, cy),
                    (cx, cy - 1),
                    (cx, cy + 1),
                ):
                    if (
                        0 <= nx < w
                        and 0 <= ny < h
                        and mask[ny][nx]
                        and not visited[idx(nx, ny)]
                    ):
                        visited[idx(nx, ny)] = 1
                        queue.append((nx, ny))

            if count > best_count:
                best_count = count
                # Pillow crop bbox is exclusive on right/bottom.
                best_bbox = (min_x, min_y, max_x + 1, max_y + 1)

    if best_bbox is None:
        raise RuntimeError("No non-transparent logo component found")

    return best_bbox


def crop_with_padding(
    image: Image.Image,
    bbox: tuple[int, int, int, int],
    padding_ratio: float = 0.08,
) -> Image.Image:
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    pad = round(max(width, height) * padding_ratio)

    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(image.width, right + pad)
    bottom = min(image.height, bottom + pad)

    return image.crop((left, top, right, bottom))


def transparent_square(image: Image.Image, size: int) -> Image.Image:
    """Scale proportionally and center on a transparent square."""

    content_size = round(size * 0.82)
    fitted = ImageOps.contain(
        image,
        (content_size, content_size),
        Image.Resampling.LANCZOS,
    )

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
    image.save(path, "PNG", optimize=True)


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)

    stacked = download(STACKED_URL)
    horizontal = download(DEFAULT_URL)

    signet_bbox = largest_connected_component_bbox(stacked)
    signet = crop_with_padding(stacked, signet_bbox)

    save_png(transparent_square(signet, 256), BRAND / "icon.png")
    save_png(transparent_square(signet, 512), BRAND / "icon@2x.png")

    save_png(proportional_logo(horizontal, 512), BRAND / "logo.png")
    save_png(proportional_logo(horizontal, 1024), BRAND / "logo@2x.png")

    # Useful review artifact; do not need to keep in final repo.
    save_png(signet, BRAND / "_source_signet_preview.png")

    print("Brand assets generated from official Octopus Energy Germany press logos:")
    for filename in (
        "icon.png",
        "icon@2x.png",
        "logo.png",
        "logo@2x.png",
        "_source_signet_preview.png",
    ):
        print(f"  {BRAND / filename}")

    print()
    print("Review _source_signet_preview.png once.")
    print("If it contains only the pink octopus signet, delete the preview file")
    print("and commit the four Home Assistant brand PNGs.")


if __name__ == "__main__":
    main()

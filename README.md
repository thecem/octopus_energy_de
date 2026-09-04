# Octopus Energy DE – Krake-only Home Assistant brand

This pack changes the Home Assistant **icon** to the official Octopus Energy
octopus signet without the wordmark.

## Official sources

Octopus Energy Germany press-assets page:

https://octopusenergy.de/newsroom/pressebilder

The page states that photos and logos are available for press download.

Source assets:

- Stacked logo:
  `https://a.storyblok.com/f/144190/826x366/e9d231e064/stacked-logo.png`
- Horizontal/default logo:
  `https://a.storyblok.com/f/144190/1293x200/461e2508f6/default-logo.png`

## Result

```text
custom_components/octopus_energy_de/brand/
├── icon.png          # octopus signet only, 256 × 256
├── icon@2x.png       # octopus signet only, 512 × 512
├── logo.png          # official horizontal logo
└── logo@2x.png       # official horizontal logo, high resolution
```

## Generate

From the repository root:

```bash
python -m pip install pillow
python scripts/fetch_brand_assets.py
```

The script:

1. downloads the official stacked logo,
2. detects the largest connected non-transparent component,
3. extracts the octopus signet without redrawing it,
4. adds only transparent padding,
5. creates 256px and 512px HA icons,
6. downloads the official horizontal logo for the full logo assets.

It also creates:

```text
brand/_source_signet_preview.png
```

Review this file once before committing. It should contain **only the pink
octopus signet**. Then delete the preview file and commit the four normal brand
files.

## Why not use the asset called “OE Logo”?

The current Octopus Energy Germany press page lists an “OE Logo”, but the
linked asset is a horizontal logo (`995x136`), not a signet-only square icon.
For Home Assistant the octopus signet from the official stacked artwork is
therefore a better source.

## Trademark

Octopus Energy names and logos remain trademarks/brand assets of their
respective owners. They are used here only to identify the third-party service
integrated by this unofficial Home Assistant project. The project is not
affiliated with or endorsed by Octopus Energy Germany.

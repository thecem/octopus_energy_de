# Brand assets

The Home Assistant brand assets in this directory are generated from official
Octopus Energy Germany press logos.

Official press page:

https://octopusenergy.de/newsroom/pressebilder

Official source assets used by `scripts/fetch_brand_assets.py`:

- Stacked logo:
  https://a.storyblok.com/f/144190/826x366/e9d231e064/stacked-logo.png
- Default horizontal logo:
  https://a.storyblok.com/f/144190/1293x200/461e2508f6/default-logo.png

Generate the PNG files from the repository root:

```bash
python -m pip install pillow
python scripts/fetch_brand_assets.py
```

Expected files:

```text
brand/
├── icon.png
├── icon@2x.png
├── logo.png
└── logo@2x.png
```

Home Assistant 2026.3+ supports local brand images for custom integrations.

Trademark notice:

Octopus Energy names and logos are trademarks/brand assets of their respective
owners. Their inclusion here is solely to identify the third-party service
integrated by this unofficial Home Assistant project. This project is not
affiliated with, endorsed by, or supported by Octopus Energy Germany.

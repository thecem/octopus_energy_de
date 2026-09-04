# Octopus Energy DE metadata & brand pack

Overlay files for:

https://github.com/thecem/octopus_energy_de

Included:

- corrected `manifest.json`
- minimal `hacs.json`
- `strings.json`
- German translation
- `services.yaml`
- HACS + Hassfest validation workflow
- official Octopus Energy DE brand source documentation
- reproducible official-logo fetch/resize script
- merge checklist

## Apply

Copy the files over the repository root while preserving paths, then run:

```bash
python -m pip install pillow
python scripts/fetch_brand_assets.py
```

Review `MERGE_CHECKLIST.md` before committing.

The brand script downloads the logo assets from Octopus Energy Germany's
official press-assets page and only resizes/pads them; it does not redraw or
alter the official artwork.

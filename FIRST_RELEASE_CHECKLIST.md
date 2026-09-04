# First release checklist

Before pushing `v0.1.0` to a new GitHub repository:

- [ ] Replace `YOUR_GITHUB_USER` in `custom_components/octopus_energy_de/manifest.json`.
- [ ] Add your GitHub username to `codeowners` in the manifest.
- [ ] Set the GitHub repository description and topics (`home-assistant`, `octopus-energy`, `germany`, `energy`).
- [ ] Run `scripts/test`.
- [ ] Run `scripts/lint` in the Dev Container.
- [ ] Start Home Assistant with `scripts/develop`.
- [ ] Add `Octopus Energy DE` through the UI and verify login/account selection.
- [ ] Compare Current Rate against the existing `octopus_germany` integration.
- [ ] Export and inspect an anonymized fixture for the test tariff.
- [ ] Add project brand assets before applying for public/default HACS inclusion.
- [ ] Create a GitHub Release (not only a tag) named `v0.1.0`.

## Suggested first Git commands

```bash
git init
git add .
git commit -m "feat: initial Octopus Energy DE release"
git branch -M main
git remote add origin git@github.com:YOUR_GITHUB_USER/octopus-energy-de.git
git push -u origin main
```

Then create the `v0.1.0` GitHub Release. The release workflow builds `octopus_energy_de.zip` automatically.

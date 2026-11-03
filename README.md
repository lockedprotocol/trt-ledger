# TRT Ledger

An independent price guide for testosterone replacement therapy (TRT):
true first-year cost of online clinics, in-person clinics near any U.S. ZIP code,
an "Am I overpaying?" calculator, and direct-to-consumer lab prices. Every price links to its source.

- `index.html`, `assets/` — the website (static; served by GitHub Pages)
- `data.json` — online clinic prices and rules for re-reading them (`data.js` is generated from it)
- `checker/` — weekly price check, self-repair, and alert emails
- `pipeline/` — monthly in-person clinic directory (NPI registry + chain locators) → `clinics/`, `geo/`
- `.github/workflows/` — the schedules that run all of the above

Owner setup and monthly checklist: [SETUP.md](SETUP.md).

Not medical advice. Clinics can't pay to be listed or ranked.

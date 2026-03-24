# Panchangam Static (GitHub Pages)

This folder is a standalone static site that can be hosted on GitHub Pages.

## What this includes

- Prebuilt JSON snapshots under `data/snapshots/`
- A manifest at `data/manifest.json`
- A static UI (`index.html` + `assets/*`)
- Optional browser-side live scrape mode:
  - `Live scrape (direct CORS)`
  - `Live scrape (CORS proxy)` via allorigins

## Important CORS note

Direct browser scraping from `https://www.panchangam.org` may fail due to CORS policy, anti-bot checks, or page shape changes. Use snapshot mode for reliable static hosting.

## Local preview

Use any static file server from this folder.

Example with Python:

```bash
cd static-gh-pages
python -m http.server 5500
```

Then open `http://localhost:5500`.

## Rebuild snapshot data

From project root:

```bash
python static-gh-pages/tools/build_snapshots.py --days 10 --cities "New York, USA" "London, UK"
```

This rewrites:

- `static-gh-pages/data/manifest.json`
- `static-gh-pages/data/snapshots/...`

## Deploy to GitHub Pages

1. Push repository.
2. In GitHub repo settings, enable Pages.
3. Set source to branch/folder containing `static-gh-pages` output.
4. If publishing from root, configure Pages path accordingly.

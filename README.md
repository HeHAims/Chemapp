# ChemApp Internal Visual Lookup

Internal visual lookup tool for furniture inventory.

## Features

- Search products by name
- Filter by category: barstools, chairs, sofas, ottomans
- Open product pages quickly
- Scrape any category page and auto-save:
  - Product name
  - Product URL
  - Product image (from product page)

## Run locally

1. Open this folder in a terminal.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start app:

```bash
python app.py
```

4. Open in browser:

http://127.0.0.1:8000

## Suggested category URLs

- Barstools: https://fwrental.com/seating/barstools
- Chairs: https://fwrental.com/seating/chairs
- Sofas: https://fwrental.com/lounge-seating/sofas
- Ottomans: https://fwrental.com/lounge-seating/ottomans-benches

## Data file

Saved inventory is in `data/inventory.json`.

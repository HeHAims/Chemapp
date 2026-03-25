# ChemApp

Internal Visual Inventory Lookup Tool for Fresh Wata Rentals. This repository contains structured JSON datasets for rental categories (barstools, chairs, sofas, cafe/console/dining, coffee tables, side tables, highboys, carts, lighting, shelving, walls, charging, and props + misc), along with frontend code for visual search and lookup.

## Features

- Structured inventory JSON files by category
- Consolidated master inventory for frontend lookup
- Search products by name and browse by category
- Product URL mapping to live rental pages

## Project Layout

- `data/inventory.json`: legacy seating inventory dataset
- `fw-inventory-lookup/data/*.json`: category datasets for lookup app
- `fw-inventory-lookup/data/master.json`: aggregated inventory dataset
- `fw-inventory-lookup/src/`: React frontend
- `app.py` and `static/`: Flask-based prototype UI

## Run Flask Prototype

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start app:

```bash
python app.py
```

3. Open:

http://127.0.0.1:8000

## Run React Lookup App

1. Go to app folder:

```bash
cd fw-inventory-lookup
```

2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm start
```

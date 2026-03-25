# FW Inventory Visual Lookup Tool

Internal tool to browse, search, and visually reference rental inventory.

## Structure

- `data/` category JSON files and `master.json`
- `images/` category folders and product subfolders
- `src/components/` reusable UI components
- `src/screens/` Home, Category, Product screens
- `src/utils/` inventory loading and search logic

## Run

```bash
npm install
npm start
```

The app runs on `http://localhost:3000` by default.

## Data Flow

- `loadMasterData()` reads from `data/master.json`
- `searchInventory(query)` returns matching products across categories
- `getProductsByCategory(category)` returns category list
- `getProductDetails(category, productName)` returns one product

## Notes

- Current dataset is seeded with starter items in each category.
- Add full inventory entries to each file in `data/` as needed.
- Place real images under `images/{category}/{product-slug}/` and update each product's `images[]` paths.

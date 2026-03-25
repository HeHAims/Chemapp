import masterData from "../data/master.json";

export const CATEGORIES = [
  "barstools",
  "chairs",
  "sofas",
  "cafe_console_dining",
  "coffee_tables",
  "side_tables",
  "highboys",
  "carts",
  "lighting",
  "shelving",
  "walls",
  "charging",
  "props_misc",
];

const GROUPS = {
  Seating: ["barstools", "chairs", "sofas"],
  "Tables + Bars": ["cafe_console_dining", "coffee_tables", "side_tables", "highboys", "carts"],
  Decor: ["lighting", "shelving", "walls", "charging"],
  Props: ["props_misc"],
};

export function loadMasterData() {
  return masterData;
}

export function searchInventory(query) {
  const normalized = query.trim().toLowerCase();
  if (!normalized) {
    return [];
  }

  const results = [];
  for (const category of CATEGORIES) {
    const products = masterData[category] || [];
    for (const product of products) {
      if ((product.name || "").toLowerCase().includes(normalized)) {
        results.push({ ...product, category });
      }
    }
  }
  return results;
}

export function getCategoryList() {
  return CATEGORIES;
}

export function getProductsByCategory(category) {
  return masterData[category] || [];
}

export function getProductDetails(category, productName) {
  const products = masterData[category] || [];
  return products.find((product) => product.name === productName) || null;
}

export function getCategoryGroups() {
  return GROUPS;
}

export function formatCategoryName(category) {
  return category
    .replace(/_/g, " ")
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

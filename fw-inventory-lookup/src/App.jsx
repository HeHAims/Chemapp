import React, { useMemo, useState } from "react";
import SearchBar from "./components/SearchBar.jsx";
import HomeScreen from "./screens/HomeScreen.jsx";
import CategoryScreen from "./screens/CategoryScreen.jsx";
import ProductScreen from "./screens/ProductScreen.jsx";
import {
  getCategoryGroups,
  getProductDetails,
  getProductsByCategory,
  searchInventory,
  formatCategoryName,
} from "./utils/inventory.js";

function App() {
  const [screen, setScreen] = useState("home");
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedProductName, setSelectedProductName] = useState(null);
  const [query, setQuery] = useState("");

  const groups = useMemo(() => getCategoryGroups(), []);
  const searchResults = useMemo(() => searchInventory(query), [query]);

  const selectedProducts = selectedCategory ? getProductsByCategory(selectedCategory) : [];
  const selectedProduct =
    selectedCategory && selectedProductName
      ? getProductDetails(selectedCategory, selectedProductName)
      : null;

  function openCategory(category) {
    setSelectedCategory(category);
    setSelectedProductName(null);
    setScreen("category");
  }

  function openProduct(product) {
    setSelectedProductName(product.name);
    setScreen("product");
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>FW Inventory Visual Lookup Tool</h1>
        <SearchBar query={query} onChange={setQuery} />
      </header>

      {query.trim() ? (
        <section className="search-results">
          <h2>Search Results</h2>
          {searchResults.length === 0 ? (
            <p>No matching inventory found.</p>
          ) : (
            <ul>
              {searchResults.map((result) => (
                <li key={`${result.category}-${result.name}`}>
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      openCategory(result.category);
                      setSelectedProductName(result.name);
                      setScreen("product");
                    }}
                  >
                    {result.name} <span>({formatCategoryName(result.category)})</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      ) : null}

      {!query.trim() && screen === "home" ? (
        <HomeScreen groups={groups} onOpenCategory={openCategory} />
      ) : null}

      {!query.trim() && screen === "category" ? (
        <CategoryScreen
          category={selectedCategory}
          products={selectedProducts}
          onSelectProduct={openProduct}
          onBack={() => setScreen("home")}
        />
      ) : null}

      {!query.trim() && screen === "product" && selectedProduct ? (
        <ProductScreen
          category={selectedCategory}
          product={selectedProduct}
          onBack={() => setScreen("category")}
        />
      ) : null}
    </div>
  );
}

export default App;

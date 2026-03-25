import React from "react";

function CategoryScreen({ category, products, onSelectProduct, onBack }) {
  return (
    <div className="category-screen">
      <div className="toolbar">
        <button type="button" onClick={onBack}>
          Back
        </button>
        <h2>{category.replace(/_/g, " ")}</h2>
      </div>

      <div className="product-grid">
        {products.map((product) => (
          <button
            type="button"
            key={product.name}
            className="product-card"
            onClick={() => onSelectProduct(product)}
          >
            <span>{product.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

export default CategoryScreen;

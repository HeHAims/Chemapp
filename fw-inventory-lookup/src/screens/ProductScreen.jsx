import React from "react";

function ProductScreen({ category, product, onBack }) {
  return (
    <div className="product-screen">
      <div className="toolbar">
        <button type="button" onClick={onBack}>
          Back
        </button>
        <h2>{category.replace(/_/g, " ")}</h2>
      </div>

      <article className="product-detail">
        <h3>{product.name}</h3>
        <p>
          <strong>Product URL:</strong>{" "}
          <a href={product.url} target="_blank" rel="noreferrer">
            {product.url}
          </a>
        </p>

        <div className="image-list">
          {product.images.map((imagePath) => (
            <div className="image-card" key={imagePath}>
              <img src={imagePath} alt={product.name} />
              <code>{imagePath}</code>
            </div>
          ))}
        </div>
      </article>
    </div>
  );
}

export default ProductScreen;

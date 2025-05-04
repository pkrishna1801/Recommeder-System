import React from 'react';
import './Catalog.css';

const Catalog = ({ products, onProductClick, browsingHistory }) => {
  // Check if products is empty or undefined
  if (!products || products.length === 0) {
    return (
      <div className="catalog-container">
        <p className="no-products-message">No products available.</p>
      </div>
    );
  }

  return (
    <div className="catalog-container">
      <div className="product-grid">
        {products.map((product) => (
          <div 
            key={product.id} 
            className={`product-card ${browsingHistory.includes(product.id) ? 'browsed' : ''}`}
            onClick={() => onProductClick(product.id)}
          >
            <div className="product-image-placeholder">
              <span className="category-label">{product.category}</span>
            </div>
            <div className="product-info">
              <h3 className="product-name">{product.name}</h3>
              <p className="product-brand">{product.brand}</p>
              <p className="product-price">${product.price.toFixed(2)}</p>
              <div className="product-rating">
                <span className="stars">{'★'.repeat(Math.round(product.rating))}</span>
                <span className="rating-number">({product.rating})</span>
              </div>
              {browsingHistory.includes(product.id) && (
                <div className="browsed-badge">Viewed</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Catalog;
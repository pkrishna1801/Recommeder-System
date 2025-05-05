import React, { useState } from 'react';
import './Catalog.css';

const Catalog = ({ products, onProductClick, browsingHistory }) => {
  // State for sorting and filtering
  const [sortBy, setSortBy] = useState('name');
  const [filterCategory, setFilterCategory] = useState('');
  
  // Get unique categories for filter dropdown
  const categories = [...new Set(products.map(product => product.category))].sort();
  
  // Sort and filter products
  const sortAndFilterProducts = () => {
    let filteredProducts = [...products];
    
    // Apply category filter if selected
    if (filterCategory) {
      filteredProducts = filteredProducts.filter(product => product.category === filterCategory);
    }
    
    // Apply sorting
    filteredProducts.sort((a, b) => {
      if (sortBy === 'price-low') {
        return a.price - b.price;
      } else if (sortBy === 'price-high') {
        return b.price - a.price;
      } else if (sortBy === 'rating') {
        return b.rating - a.rating;
      } else {
        // Default sort by name
        return a.name.localeCompare(b.name);
      }
    });
    
    return filteredProducts;
  };
  
  // Handle product click
  const handleProductClick = (productId) => {
    if (onProductClick) {
      onProductClick(productId);
    }
  };
  
  // Check if a product is in browsing history
  const isInBrowsingHistory = (productId) => {
    return browsingHistory.includes(productId);
  };

  return (
    <div className="catalog-container">
      <div className="catalog-controls">
        <div className="filter-control">
          <label htmlFor="category-filter">Filter by Category:</label>
          <select 
            id="category-filter" 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
        
        <div className="sort-control">
          <label htmlFor="sort-by">Sort by:</label>
          <select 
            id="sort-by" 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="name">Name (A-Z)</option>
            <option value="price-low">Price (Low to High)</option>
            <option value="price-high">Price (High to Low)</option>
            <option value="rating">Rating (High to Low)</option>
          </select>
        </div>
      </div>
      
      <div className="products-grid">
        {sortAndFilterProducts().map(product => (
          <div 
            key={product.id} 
            className={`product-card ${isInBrowsingHistory(product.id) ? 'viewed' : ''}`}
            onClick={() => handleProductClick(product.id)}
          >
            {isInBrowsingHistory(product.id) && (
              <div className="viewed-badge">Viewed</div>
            )}
            
            <div className="product-image">
              {/* Use a placeholder based on category */}
              <div className="placeholder-image">
                {product.category.charAt(0)}
              </div>
            </div>
            
            <div className="product-info">
              <h3 className="product-name">{product.name}</h3>
              <div className="product-category">{product.category} / {product.subcategory}</div>
              <div className="product-brand">{product.brand}</div>
              
              <div className="product-rating">
                {'★'.repeat(Math.floor(product.rating))}
                {'☆'.repeat(5 - Math.floor(product.rating))}
                <span className="rating-value"> ({product.rating})</span>
              </div>
              
              <div className="product-price">${product.price.toFixed(2)}</div>
              
              {product.tags && (
                <div className="product-tags">
                  {product.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Catalog;
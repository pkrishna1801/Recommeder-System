import React, { useState, useEffect } from 'react';
import '../styles/App.css';

const Catalog = ({ products, onProductClick, browsingHistory }) => {
  // State for filtered products
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [filterCategory, setFilterCategory] = useState('');
  const [sortOption, setSortOption] = useState('name');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Categories for filter dropdown
  const [categories, setCategories] = useState([]);
  
  // Apply filtering and sorting when products, filters, or sort options change
  useEffect(() => {
    if (!products || products.length === 0) {
      setFilteredProducts([]);
      return;
    }
    
    // Extract unique categories
    const uniqueCategories = [...new Set(products.map(p => p.category))].sort();
    setCategories(uniqueCategories);
    
    // Apply filtering by category
    let result = [...products];
    
    if (filterCategory) {
      result = result.filter(p => p.category === filterCategory);
    }
    
    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      result = result.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.brand.toLowerCase().includes(query) ||
        (p.tags && p.tags.some(tag => tag.toLowerCase().includes(query)))
      );
    }
    
    // Apply sorting
    result.sort((a, b) => {
      switch (sortOption) {
        case 'price-low':
          return a.price - b.price;
        case 'price-high':
          return b.price - a.price;
        case 'rating':
          return b.rating - a.rating;
        case 'name':
        default:
          return a.name.localeCompare(b.name);
      }
    });
    
    setFilteredProducts(result);
  }, [products, filterCategory, sortOption, searchQuery]);
  
  // Reset filters
  const handleResetFilters = () => {
    setFilterCategory('');
    setSortOption('name');
    setSearchQuery('');
  };
  
  // Loading state
  if (!products || products.length === 0) {
    return <div className="catalog-loading">Loading products...</div>;
  }

  return (
    <div className="catalog-container">
      <div className="catalog-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-controls">
          <select 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
            className="filter-select"
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
          
          <select 
            value={sortOption} 
            onChange={(e) => setSortOption(e.target.value)}
            className="sort-select"
          >
            <option value="name">Sort by Name</option>
            <option value="price-low">Price: Low to High</option>
            <option value="price-high">Price: High to Low</option>
            <option value="rating">Highest Rated</option>
          </select>
          
          <button 
            className="reset-filters-btn"
            onClick={handleResetFilters}
          >
            Reset
          </button>
        </div>
      </div>
      
      <div className="filter-summary">
        <span className="results-count">{filteredProducts.length} products</span>
        {(filterCategory || searchQuery) && (
          <div className="active-filters">
            {filterCategory && (
              <span className="filter-tag">
                Category: {filterCategory}
              </span>
            )}
            {searchQuery && (
              <span className="filter-tag">
                Search: "{searchQuery}"
              </span>
            )}
          </div>
        )}
      </div>
      
      <div className="product-grid">
        {filteredProducts.length > 0 ? (
          filteredProducts.map((product) => (
            <div 
              key={product.id}
              className={`product-card ${browsingHistory.includes(product.id) ? 'browsed' : ''}`}
              onClick={() => onProductClick(product.id)}
            >
              <div className="product-image">
                {/* Placeholder for product image */}
                <div className="image-placeholder">
                  <span>{product.category}</span>
                </div>
              </div>
              <div className="product-info">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-brand">{product.brand}</p>
                <p className="product-price">${product.price.toFixed(2)}</p>
                <div className="product-rating">
                  Rating: {product.rating} ★
                </div>
                <div className="product-tags">
                  {product.tags && product.tags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
              {browsingHistory.includes(product.id) && (
                <div className="browsed-badge">Viewed</div>
              )}
            </div>
          ))
        ) : (
          <div className="no-products">
            <p>No products match your current filters. Try adjusting your search or filters.</p>
            <button 
              className="reset-filters-btn"
              onClick={handleResetFilters}
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Catalog;
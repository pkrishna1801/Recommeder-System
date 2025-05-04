import React, { useState, useEffect } from 'react';
import './UserPreferences.css';

const UserPreferences = ({ preferences, products, onPreferencesChange }) => {
  // Extract unique categories and brands from products
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  
  // Local state for form inputs
  const [selectedCategories, setSelectedCategories] = useState(preferences.categories || []);
  const [selectedBrands, setSelectedBrands] = useState(preferences.brands || []);
  const [priceRange, setPriceRange] = useState(preferences.priceRange || 'all');
  
  // Extract unique categories and brands when products change
  useEffect(() => {
    if (products && products.length) {
      // Extract unique categories
      const uniqueCategories = [...new Set(products.map(p => p.category))].filter(Boolean).sort();
      setCategories(uniqueCategories);
      
      // Extract unique brands
      const uniqueBrands = [...new Set(products.map(p => p.brand))].filter(Boolean).sort();
      setBrands(uniqueBrands);
    }
  }, [products]);
  
  // Update preferences when form inputs change
  const handleCategoryChange = (category) => {
    const newCategories = selectedCategories.includes(category)
      ? selectedCategories.filter(c => c !== category) // Remove if already selected
      : [...selectedCategories, category]; // Add if not selected
    
    setSelectedCategories(newCategories);
    onPreferencesChange({ ...preferences, categories: newCategories });
  };
  
  const handleBrandChange = (brand) => {
    const newBrands = selectedBrands.includes(brand)
      ? selectedBrands.filter(b => b !== brand) // Remove if already selected
      : [...selectedBrands, brand]; // Add if not selected
    
    setSelectedBrands(newBrands);
    onPreferencesChange({ ...preferences, brands: newBrands });
  };
  
  const handlePriceRangeChange = (e) => {
    const newPriceRange = e.target.value;
    setPriceRange(newPriceRange);
    onPreferencesChange({ ...preferences, priceRange: newPriceRange });
  };
  
  const clearAllPreferences = () => {
    setSelectedCategories([]);
    setSelectedBrands([]);
    setPriceRange('all');
    onPreferencesChange({ categories: [], brands: [], priceRange: 'all' });
  };
  
  return (
    <div className="preferences-container">
      <div className="preferences-header">
        <h3>Your Preferences</h3>
        <button className="clear-preferences-btn" onClick={clearAllPreferences}>Clear All</button>
      </div>
      
      <div className="preference-section">
        <h4>Price Range</h4>
        <div className="price-range-selector">
          <select value={priceRange} onChange={handlePriceRangeChange}>
            <option value="all">All Prices</option>
            <option value="0-50">Under $50</option>
            <option value="50-100">$50 - $100</option>
            <option value="100+">$100 and up</option>
          </select>
        </div>
      </div>
      
      <div className="preference-section">
        <h4>Categories</h4>
        <div className="checkbox-group">
          {categories.map(category => (
            <label key={category} className="checkbox-item">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category)}
                onChange={() => handleCategoryChange(category)}
              />
              {category}
            </label>
          ))}
        </div>
      </div>
      
      <div className="preference-section">
        <h4>Brands</h4>
        <div className="checkbox-group">
          {brands.map(brand => (
            <label key={brand} className="checkbox-item">
              <input
                type="checkbox"
                checked={selectedBrands.includes(brand)}
                onChange={() => handleBrandChange(brand)}
              />
              {brand}
            </label>
          ))}
        </div>
      </div>
      
      <div className="selected-preferences">
        <h4>Selected Preferences</h4>
        {selectedCategories.length === 0 && selectedBrands.length === 0 && priceRange === 'all' ? (
          <p className="no-preferences">No preferences selected</p>
        ) : (
          <ul className="preferences-summary">
            {priceRange !== 'all' && (
              <li>Price: {priceRange}</li>
            )}
            {selectedCategories.length > 0 && (
              <li>Categories: {selectedCategories.join(', ')}</li>
            )}
            {selectedBrands.length > 0 && (
              <li>Brands: {selectedBrands.join(', ')}</li>
            )}
          </ul>
        )}
      </div>
    </div>
  );
};

export default UserPreferences;
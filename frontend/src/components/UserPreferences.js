import React, { useState, useEffect } from 'react';
import './UserPreferences.css';

const UserPreferences = ({ preferences, products, onPreferencesChange }) => {
  // State for form values
  const [formValues, setFormValues] = useState({
    priceRange: preferences.priceRange || 'all',
    categories: preferences.categories || [],
    brands: preferences.brands || []
  });
  
  // Get unique categories and brands from products
  const categories = [...new Set(products.map(product => product.category))].sort();
  const brands = [...new Set(products.map(product => product.brand))].sort();
  
  // Price range options
  const priceRanges = [
    { id: 'all', label: 'All Prices' },
    { id: '0-50', label: 'Under $50' },
    { id: '50-100', label: 'Between $50-$100' },
    { id: '100-200', label: 'Between $100-$200' },
    { id: '200+', label: 'Over $200' }
  ];
  
  // Update parent component when form values change
  useEffect(() => {
    if (onPreferencesChange) {
      onPreferencesChange(formValues);
    }
  }, [formValues, onPreferencesChange]);
  
  // Handle price range change
  const handlePriceRangeChange = (e) => {
    setFormValues({
      ...formValues,
      priceRange: e.target.value
    });
  };
  
  // Handle category selection
  const handleCategoryChange = (category, isChecked) => {
    let updatedCategories;
    
    if (isChecked) {
      // Add category
      updatedCategories = [...formValues.categories, category];
    } else {
      // Remove category
      updatedCategories = formValues.categories.filter(cat => cat !== category);
    }
    
    setFormValues({
      ...formValues,
      categories: updatedCategories
    });
  };
  
  // Handle brand selection
  const handleBrandChange = (brand, isChecked) => {
    let updatedBrands;
    
    if (isChecked) {
      // Add brand
      updatedBrands = [...formValues.brands, brand];
    } else {
      // Remove brand
      updatedBrands = formValues.brands.filter(b => b !== brand);
    }
    
    setFormValues({
      ...formValues,
      brands: updatedBrands
    });
  };
  
  // Clear all preferences
  const handleClearAll = () => {
    setFormValues({
      priceRange: 'all',
      categories: [],
      brands: []
    });
  };

  return (
    <div className="preferences-container">
      <div className="preferences-header">
        <h3>Your Preferences</h3>
        <button 
          className="clear-btn" 
          onClick={handleClearAll}
          title="Clear all preferences"
        >
          Clear All
        </button>
      </div>
      
      <div className="preference-section">
        <h4>Price Range</h4>
        <div className="price-ranges">
          {priceRanges.map(range => (
            <div key={range.id} className="price-range-option">
              <input
                type="radio"
                id={`price-${range.id}`}
                name="priceRange"
                value={range.id}
                checked={formValues.priceRange === range.id}
                onChange={handlePriceRangeChange}
              />
              <label htmlFor={`price-${range.id}`}>{range.label}</label>
            </div>
          ))}
        </div>
      </div>
      
      <div className="preference-section">
        <h4>Categories</h4>
        <div className="categories-container">
          {categories.map(category => (
            <div key={category} className="category-option">
              <input
                type="checkbox"
                id={`category-${category}`}
                checked={formValues.categories.includes(category)}
                onChange={(e) => handleCategoryChange(category, e.target.checked)}
              />
              <label htmlFor={`category-${category}`}>{category}</label>
            </div>
          ))}
        </div>
      </div>
      
      <div className="preference-section">
        <h4>Brands</h4>
        <div className="brands-container">
          {brands.map(brand => (
            <div key={brand} className="brand-option">
              <input
                type="checkbox"
                id={`brand-${brand}`}
                checked={formValues.brands.includes(brand)}
                onChange={(e) => handleBrandChange(brand, e.target.checked)}
              />
              <label htmlFor={`brand-${brand}`}>{brand}</label>
            </div>
          ))}
        </div>
      </div>
      
      <div className="preferences-summary">
        <h4>Selected Preferences:</h4>
        <ul>
          <li>
            <strong>Price Range:</strong> {
              priceRanges.find(range => range.id === formValues.priceRange)?.label || 'All Prices'
            }
          </li>
          <li>
            <strong>Categories:</strong> {
              formValues.categories.length > 0 
                ? formValues.categories.join(', ') 
                : 'All Categories'
            }
          </li>
          <li>
            <strong>Brands:</strong> {
              formValues.brands.length > 0 
                ? formValues.brands.join(', ') 
                : 'All Brands'
            }
          </li>
        </ul>
      </div>
    </div>
  );
};

export default UserPreferences;
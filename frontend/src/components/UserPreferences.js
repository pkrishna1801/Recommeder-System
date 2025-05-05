import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchProductCategories, fetchProductBrands, fetchPriceRange } from '../services/api';
import '../styles/UserPreferences.css';

const UserPreferences = () => {
  // Get user preferences from auth context
  const { preferences, updatePreferences, token } = useAuth();
  
  // Local state for UI elements
  const [categories, setCategories] = useState([]);
  const [brands, setBreedInds] = useState([]);
  const [priceRange, setPriceRange] = useState({ min: 0, max: 1000 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Price range options for dropdown
  const priceRangeOptions = [
    { label: 'All Prices', min: null, max: null },
    { label: 'Under $50', min: 0, max: 50 },
    { label: '$50 to $100', min: 50, max: 100 },
    { label: '$100 to $200', min: 100, max: 200 },
    { label: 'Over $200', min: 200, max: null }
  ];
  
  // Load categories, brands, and price range on component mount
  useEffect(() => {
    const loadFilterOptions = async () => {
      setLoading(true);
      try {
        // Load categories
        const categoriesResponse = await fetchProductCategories();
        if (categoriesResponse.success) {
          setCategories(categoriesResponse.categories);
        }
        
        // Load brands
        const brandsResponse = await fetchProductBrands();
        if (brandsResponse.success) {
          setBreedInds(brandsResponse.brands);
        }
        
        // Load price range
        const priceRangeResponse = await fetchPriceRange();
        if (priceRangeResponse.success) {
          setPriceRange(priceRangeResponse.price_range);
        }
      } catch (err) {
        setError('Error loading filter options');
        console.error('Error loading filter options:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadFilterOptions();
  }, []);
  
  // Handle price range selection
  const handlePriceRangeChange = (e) => {
    const selectedOption = priceRangeOptions.find(option => 
      `${option.min}-${option.max}` === e.target.value
    );
    
    if (selectedOption) {
      updatePreferences({ 
        price_range: { 
          min: selectedOption.min, 
          max: selectedOption.max 
        } 
      });
    }
  };
  
  // Get current price range value for select element
  const getCurrentPriceRangeValue = () => {
    const { min, max } = preferences.price_range || {};
    
    // Find matching option or default to 'All Prices'
    const matchingOption = priceRangeOptions.find(option => 
      option.min === min && option.max === max
    );
    
    return matchingOption 
      ? `${matchingOption.min}-${matchingOption.max}` 
      : 'null-null';
  };
  
  // Handle category selection
  const handleCategoryChange = (e) => {
    const category = e.target.value;
    const isChecked = e.target.checked;
    
    let updatedCategories;
    if (isChecked) {
      // Add category if checked
      updatedCategories = [...(preferences.category_preferences || []), category];
    } else {
      // Remove category if unchecked
      updatedCategories = (preferences.category_preferences || []).filter(c => c !== category);
    }
    
    updatePreferences({ category_preferences: updatedCategories });
  };
  
  // Handle brand selection
  const handleBrandChange = (e) => {
    const brand = e.target.value;
    const isChecked = e.target.checked;
    
    let updatedBrands;
    if (isChecked) {
      // Add brand if checked
      updatedBrands = [...(preferences.brand_preferences || []), brand];
    } else {
      // Remove brand if unchecked
      updatedBrands = (preferences.brand_preferences || []).filter(b => b !== brand);
    }
    
    updatePreferences({ brand_preferences: updatedBrands });
  };

  if (loading) {
    return <div className="preferences-loading">Loading preferences...</div>;
  }

  if (error) {
    return <div className="preferences-error">{error}</div>;
  }

  return (
    <div className="preferences-container">
      <h3 className="preferences-title">Your Preferences</h3>
      
      {/* Price Range Preferences */}
      <div className="preference-section">
        <h4>Price Range</h4>
        <select 
          value={getCurrentPriceRangeValue()} 
          onChange={handlePriceRangeChange}
          className="price-range-select"
        >
          {priceRangeOptions.map(option => (
            <option 
              key={`${option.min}-${option.max}`} 
              value={`${option.min}-${option.max}`}
            >
              {option.label}
            </option>
          ))}
        </select>
      </div>
      
      {/* Category Preferences */}
      <div className="preference-section">
        <h4>Categories</h4>
        <div className="checkbox-container">
          {categories.map(category => (
            <label key={category} className="checkbox-label">
              <input
                type="checkbox"
                value={category}
                checked={(preferences.category_preferences || []).includes(category)}
                onChange={handleCategoryChange}
              />
              {category}
            </label>
          ))}
        </div>
      </div>
      
      {/* Brand Preferences */}
      <div className="preference-section">
        <h4>Brands</h4>
        <div className="checkbox-container">
          {brands.map(brand => (
            <label key={brand} className="checkbox-label">
              <input
                type="checkbox"
                value={brand}
                checked={(preferences.brand_preferences || []).includes(brand)}
                onChange={handleBrandChange}
              />
              {brand}
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default UserPreferences;
import React, { useState, useEffect } from 'react';
import './styles/App.css';
import Catalog from './components/Catalog';
import UserPreferences from './components/UserPreferences';
import Recommendations from './components/Recommendations';
import BrowsingHistory from './components/BrowsingHistory';
import { fetchProducts, getRecommendations } from './services/api';

function App() {
  // State for products catalog
  const [products, setProducts] = useState([]);
  const [isProductsLoading, setIsProductsLoading] = useState(true);
  const [productError, setProductError] = useState(null);
  
  // State for user preferences
  const [userPreferences, setUserPreferences] = useState({
    priceRange: 'all',
    categories: [],
    brands: []
  });
  
  // State for browsing history
  const [browsingHistory, setBrowsingHistory] = useState([]);
  
  // State for recommendations
  const [recommendations, setRecommendations] = useState([]);
  
  // State for loading status
  const [isRecommendationsLoading, setIsRecommendationsLoading] = useState(false);
  
  // Fetch products on component mount
  useEffect(() => {
    const loadProducts = async () => {
      try {
        setIsProductsLoading(true);
        setProductError(null);
        const productsData = await fetchProducts();
        setProducts(productsData);
      } catch (error) {
        console.error('Error fetching products:', error);
        setProductError('Failed to load products. Please try again later.');
      } finally {
        setIsProductsLoading(false);
      }
    };
    
    loadProducts();
  }, []);
  
  // Handle product click to add to browsing history
  const handleProductClick = (productId) => {
    // Avoid duplicates in browsing history
    if (!browsingHistory.includes(productId)) {
      setBrowsingHistory([...browsingHistory, productId]);
    }
  };
  
  // Update user preferences
  const handlePreferencesChange = (newPreferences) => {
    setUserPreferences(prevPreferences => ({
      ...prevPreferences,
      ...newPreferences
    }));
  };
  
  // Get recommendations based on preferences and browsing history
  const handleGetRecommendations = async () => {
    if (isRecommendationsLoading) return; // Prevent multiple requests
    
    setIsRecommendationsLoading(true);
    try {
      const recommendationsData = await getRecommendations(userPreferences, browsingHistory);
      setRecommendations(recommendationsData);
    } catch (error) {
      console.error('Error getting recommendations:', error);
      // Could add error state and display if needed
    } finally {
      setIsRecommendationsLoading(false);
    }
  };
  
  // Clear browsing history
  const handleClearHistory = () => {
    setBrowsingHistory([]);
  };
  
  return (
    <div className="app">
      <header className="app-header">
        <h1>AI-Powered Product Recommendation Engine</h1>
        <p className="app-description">
          Browse products, set your preferences, and get personalized recommendations
        </p>
      </header>
      
      <main className="app-content">
        <div className="user-section">
          <UserPreferences 
            preferences={userPreferences}
            products={products}
            onPreferencesChange={handlePreferencesChange}
          />
          
          <BrowsingHistory 
            history={browsingHistory}
            products={products}
            onClearHistory={handleClearHistory}
          />
          
          <button 
            className="get-recommendations-btn"
            onClick={handleGetRecommendations}
            disabled={isRecommendationsLoading || browsingHistory.length === 0}
          >
            {isRecommendationsLoading ? 'Getting Recommendations...' : 'Get Personalized Recommendations'}
          </button>
        </div>
        
        <div className="catalog-section">
          <div className="section-header">
            <h2>Product Catalog</h2>
            {isProductsLoading && <span className="loading-indicator">Loading...</span>}
          </div>
          
          {productError ? (
            <div className="error-message">{productError}</div>
          ) : (
            <Catalog 
              products={products}
              onProductClick={handleProductClick}
              browsingHistory={browsingHistory}
            />
          )}
        </div>
        
        <div className="recommendations-section">
          <h2>Your Recommendations</h2>
          <Recommendations 
            recommendations={recommendations}
            isLoading={isRecommendationsLoading}
          />
        </div>
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2025 AI-Powered Product Recommendations</p>
      </footer>
    </div>
  );
}

export default App;
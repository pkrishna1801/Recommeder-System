import React, { useState, useEffect } from 'react';
import './styles/App.css';
import Catalog from './components/Catalog';
import UserPreferences from './components/UserPreferences';
import Recommendations from './components/Recommendations';
import BrowsingHistory from './components/BrowsingHistory';
import UserProfile from './components/UserProfile';
import AuthPage from './components/AuthPage';
import { 
  fetchProducts, 
  getRecommendations, 
  addToBrowsingHistory, 
  getUserBrowsingHistory,
  clearBrowsingHistory 
} from './services/api';
import { AuthProvider, useAuth } from './context/AuthContext';

// Main App component wrapped with auth provider
const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

const AppContent = () => {
  // Auth context
  const { isAuthenticated, token, preferences, updatePreferences } = useAuth();
  
  // State for products catalog
  const [products, setProducts] = useState([]);
  
  // State for browsing history (keeping local copy for non-authenticated users)
  const [browsingHistory, setBrowsingHistory] = useState([]);
  
  // State for recommendations
  const [recommendations, setRecommendations] = useState([]);
  
  // State for loading status
  const [isLoading, setIsLoading] = useState(false);
  
  // State for mobile responsive design
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // State for current page view
  const [currentPage, setCurrentPage] = useState('catalog'); // 'catalog' or 'recommendations'
  
  // Fetch products on component mount
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const data = await fetchProducts();
        setProducts(data.products || []);
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };
    
    loadProducts();
  }, []);
  
  // Sync browsing history with server when authenticated
  useEffect(() => {
    const syncBrowsingHistory = async () => {
      if (isAuthenticated && token) {
        try {
          const response = await getUserBrowsingHistory(token);
          if (response.success && response.browsing_history) {
            setBrowsingHistory(response.browsing_history);
          }
        } catch (error) {
          console.error('Error syncing browsing history:', error);
        }
      }
    };
    
    if (isAuthenticated && token && products.length > 0) {
      syncBrowsingHistory();
    }
  }, [isAuthenticated, token, products]);
  
  // Handle product click to add to browsing history
  const handleProductClick = async (productId) => {
    // Add to local browsing history if not already there
    if (!browsingHistory.includes(productId)) {
      setBrowsingHistory(prevHistory => [productId, ...prevHistory]);
    }
    
    // If authenticated, save to server
    if (isAuthenticated && token) {
      try {
        const response = await addToBrowsingHistory(productId, token);
        if (response.success && response.browsing_history) {
          // Update local state with server response to ensure consistency
          setBrowsingHistory(response.browsing_history);
        }
      } catch (error) {
        console.error('Error saving browsing history:', error);
      }
    }
  };
  
  // Get recommendations based on preferences and browsing history
  const handleGetRecommendations = async () => {
    setIsLoading(true);
    try {
      const data = await getRecommendations(
        preferences, 
        browsingHistory,
        isAuthenticated ? token : null
      );
      setRecommendations(data.recommendations || []);
      // Switch to recommendations page after loading
      setCurrentPage('recommendations');
    } catch (error) {
      console.error('Error getting recommendations:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Clear browsing history
  const handleClearHistory = async () => {
    // Clear local browsing history
    setBrowsingHistory([]);
    
    // Clear server browsing history if authenticated
    if (isAuthenticated && token) {
      try {
        await clearBrowsingHistory(token);
      } catch (error) {
        console.error('Error clearing browsing history on server:', error);
      }
    }
  };

  // Toggle mobile menu
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  // If not authenticated, show auth page
  if (!isAuthenticated) {
    return <AuthPage />;
  }
  
  // Main app UI for authenticated users
  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>AI Product Recommendations</h1>
          <button 
            className="mobile-menu-toggle" 
            onClick={toggleMobileMenu}
            aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
          >
            <span className="menu-icon"></span>
          </button>
        </div>
        <UserProfile />
        <div className="page-navigation">
          <button 
            className={`nav-button ${currentPage === 'catalog' ? 'active' : ''}`}
            onClick={() => setCurrentPage('catalog')}
          >
            Product Catalog
          </button>
          <button 
            className={`nav-button ${currentPage === 'recommendations' ? 'active' : ''}`}
            onClick={() => {
              if (recommendations.length > 0) {
                setCurrentPage('recommendations');
              } else {
                handleGetRecommendations();
              }
            }}
          >
            Your Recommendations
          </button>
        </div>
      </header>
      
      <main className={`app-content ${isMobileMenuOpen ? 'mobile-menu-open' : ''}`}>
        <div className="sidebar">
          <UserPreferences />
          
          <BrowsingHistory 
            products={products}
            browsingHistory={browsingHistory}
            onClearHistory={handleClearHistory}
          />
          
          <button 
            className="get-recommendations-btn"
            onClick={handleGetRecommendations}
            disabled={isLoading}
          >
            {isLoading ? 'Getting Recommendations...' : 'Get Personalized Recommendations'}
          </button>
        </div>
        
        <div className="main-content">
          {currentPage === 'catalog' ? (
            <section className="catalog-section">
              <h2 className="section-title">Product Catalog</h2>
              <Catalog 
                products={products}
                onProductClick={handleProductClick}
                browsingHistory={browsingHistory}
              />
            </section>
          ) : (
            <section className="recommendations-section full-page">
              <h2 className="section-title">Your Recommendations</h2>
              <Recommendations 
                recommendations={recommendations}
                isLoading={isLoading}
              />
            </section>
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
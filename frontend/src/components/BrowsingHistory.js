import React from 'react';
import './BrowsingHistory.css';

const BrowsingHistory = ({ history, products, onClearHistory }) => {
  // Get full product details for each ID in history
  const getHistoryProducts = () => {
    if (!history || !products) return [];
    
    // Create product lookup for efficiency
    const productLookup = {};
    products.forEach(product => {
      productLookup[product.id] = product;
    });
    
    // Map history IDs to products (reverse to show most recent first)
    return [...history]
      .reverse()
      .map(id => productLookup[id])
      .filter(product => product !== undefined); // Filter out any IDs that don't match products
  };
  
  const historyProducts = getHistoryProducts();
  
  // Handle clear history button click
  const handleClearHistory = () => {
    if (onClearHistory) {
      onClearHistory();
    }
  };

  return (
    <div className="history-container">
      <div className="history-header">
        <h3>Your Browsing History</h3>
        {historyProducts.length > 0 && (
          <button 
            className="clear-history-btn" 
            onClick={handleClearHistory}
            title="Clear browsing history"
          >
            Clear
          </button>
        )}
      </div>
      
      {historyProducts.length === 0 ? (
        <div className="empty-history">
          <p>No browsing history yet. Click on products to add them here.</p>
        </div>
      ) : (
        <div className="history-items">
          {historyProducts.map(product => (
            <div key={product.id} className="history-item">
              <div className="history-item-image">
                {/* Placeholder for product image */}
                <div className="history-placeholder">{product.category.charAt(0)}</div>
              </div>
              <div className="history-item-info">
                <h4 className="history-item-name">{product.name}</h4>
                <div className="history-item-category">{product.category}</div>
                <div className="history-item-price">${product.price.toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {historyProducts.length > 0 && (
        <div className="history-summary">
          <p>Browse patterns: {getSummary(historyProducts)}</p>
        </div>
      )}
    </div>
  );
};

// Helper function to generate a summary of browsing patterns
const getSummary = (products) => {
  // Count categories
  const categoryCounts = {};
  products.forEach(product => {
    const category = product.category;
    categoryCounts[category] = (categoryCounts[category] || 0) + 1;
  });
  
  // Find most viewed category
  let mostViewedCategory = '';
  let highestCount = 0;
  
  Object.entries(categoryCounts).forEach(([category, count]) => {
    if (count > highestCount) {
      mostViewedCategory = category;
      highestCount = count;
    }
  });
  
  // Calculate average price
  const totalPrice = products.reduce((sum, product) => sum + product.price, 0);
  const avgPrice = totalPrice / products.length;
  
  return `Most viewed: ${mostViewedCategory}, Avg. price: $${avgPrice.toFixed(2)}`;
};

export default BrowsingHistory;
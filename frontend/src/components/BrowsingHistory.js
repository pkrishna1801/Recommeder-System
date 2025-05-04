import React from 'react';
import './BrowsingHistory.css';

const BrowsingHistory = ({ history, products, onClearHistory }) => {
  // If no browsing history, display empty state
  if (!history || history.length === 0) {
    return (
      <div className="history-container">
        <div className="history-header">
          <h3>Your Browsing History</h3>
        </div>
        <p className="no-history-message">No browsing history yet. Click on products to add them here.</p>
      </div>
    );
  }

  // Get the full product details for each product in the browsing history
  const historyProducts = history.map(productId => {
    return products.find(product => product.id === productId);
  }).filter(Boolean); // Filter out any undefined products
  
  return (
    <div className="history-container">
      <div className="history-header">
        <h3>Your Browsing History ({historyProducts.length})</h3>
        <button 
          className="clear-history-btn"
          onClick={onClearHistory}
        >
          Clear History
        </button>
      </div>
      
      <div className="history-items">
        {historyProducts.slice().reverse().map(product => (
          <div key={product.id} className="history-item">
            <div className="history-item-icon">
              <span>{product.category.charAt(0)}</span>
            </div>
            <div className="history-item-details">
              <p className="history-item-name">{product.name}</p>
              <p className="history-item-price">${product.price.toFixed(2)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BrowsingHistory;
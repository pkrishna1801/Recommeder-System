import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/BrowsingHistory.css';

const BrowsingHistory = ({ products, browsingHistory, onClearHistory }) => {
  const { token, isAuthenticated } = useAuth();
  const [historyProducts, setHistoryProducts] = useState([]);
  const [expanded, setExpanded] = useState(true);
  
  // Map browsing history IDs to full product objects whenever products or browsingHistory change
  useEffect(() => {
    if (!products || products.length === 0 || !browsingHistory) return;
    
    // Create a product lookup map for faster access
    const productMap = {};
    products.forEach(product => {
      productMap[product.id] = product;
    });
    
    // Map browsing history IDs to product objects
    const historyItems = browsingHistory
      .map(productId => productMap[productId])
      .filter(product => product !== undefined); // Filter out any undefined products
    
    setHistoryProducts(historyItems);
  }, [products, browsingHistory]);
  
  // Toggle the expanded state
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };

  if (historyProducts.length === 0) {
    return (
      <div className="history-container">
        <div className="history-header">
          <h3>Your Browsing History</h3>
          <button className="expand-button" onClick={toggleExpanded}>
            {expanded ? '−' : '+'}
          </button>
        </div>
        {expanded && (
          <div className="history-empty">
            <p>You haven't viewed any products yet. Click on products to add them to your history.</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h3>Your Browsing History</h3>
        <div className="history-actions">
          <button 
            className="clear-history-btn"
            onClick={onClearHistory}
          >
            Clear All
          </button>
          <button className="expand-button" onClick={toggleExpanded}>
            {expanded ? '−' : '+'}
          </button>
        </div>
      </div>
      
      {expanded && (
        <div className="history-items">
          {historyProducts.map((product) => (
            <div key={product.id} className="history-item">
              <div className="history-item-image">
                {/* Placeholder for product image */}
                <div className="image-placeholder-small">
                  <span>{product.category ? product.category.charAt(0) : '?'}</span>
                </div>
              </div>
              <div className="history-item-info">
                <p className="history-item-name">{product.name}</p>
                <div className="history-item-details">
                  <span className="history-item-price">${product.price.toFixed(2)}</span>
                  <span className="history-item-brand">{product.brand}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BrowsingHistory;
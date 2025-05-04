import React from 'react';
import './Recommendations.css';

const Recommendations = ({ recommendations, isLoading }) => {
  // Display loading state
  if (isLoading) {
    return (
      <div className="recommendations-container loading">
        <div className="loading-animation">
          <div className="spinner"></div>
          <p>Generating personalized recommendations...</p>
        </div>
      </div>
    );
  }
  
  // Display empty state if no recommendations
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <div className="empty-recommendations">
          <h3>No Recommendations Yet</h3>
          <p>Set your preferences and browse some products to get personalized recommendations.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="recommendations-container">
      <div className="recommendations-grid">
        {recommendations.map((rec, index) => (
          <div className="recommendation-card" key={rec.product.id}>
            <div className="recommendation-rank">{index + 1}</div>
            
            <div className="recommendation-header">
              <h3 className="recommendation-title">{rec.product.name}</h3>
              <div className="recommendation-score">
                <div 
                  className="score-bar" 
                  style={{ width: `${rec.relevance_score * 100}%` }}
                ></div>
                <span className="score-value">{Math.round(rec.relevance_score * 100)}%</span>
              </div>
            </div>
            
            <div className="recommendation-content">
              <div className="product-details">
                <div className="product-image-placeholder">
                  <span>{rec.product.category.charAt(0)}</span>
                </div>
                
                <div className="product-info">
                  <p className="product-category">{rec.product.category} / {rec.product.subcategory}</p>
                  <p className="product-brand">{rec.product.brand}</p>
                  <p className="product-price">${rec.product.price.toFixed(2)}</p>
                  <div className="product-rating">
                    <span className="stars">{'★'.repeat(Math.round(rec.product.rating))}</span>
                    <span className="rating-value">({rec.product.rating})</span>
                  </div>
                </div>
              </div>
              
              <div className="recommendation-explanation">
                <h4>Why We Recommend This:</h4>
                <p>{rec.explanation}</p>
              </div>
              
              <div className="product-tags">
                {rec.product.tags && rec.product.tags.map(tag => (
                  <span className="tag" key={tag}>{tag}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Recommendations;
import React from 'react';
import '../styles/Recommendations.css';

const Recommendations = ({ recommendations, isLoading }) => {
  if (isLoading) {
    return (
      <div className="recommendations-container loading">
        <div className="loader-container">
          <div className="loader"></div>
          <p>Generating personalized recommendations...</p>
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="#e0e0e0" strokeWidth="2"/>
              <path d="M8 12H16" stroke="#e0e0e0" strokeWidth="2" strokeLinecap="round"/>
              <path d="M12 8V16" stroke="#e0e0e0" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </div>
          <h3>No recommendations yet</h3>
          <p>Browse some products and set your preferences to get personalized recommendations.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <p>Based on your preferences and browsing history, we think you'll love these products:</p>
      </div>
      
      {recommendations.map((recommendation, index) => (
        <div key={recommendation.product.id} className="recommendation-card">
          <div className="recommendation-rank">
            <span className="rank-number">#{index + 1}</span>
          </div>
          
          <div className="recommendation-content">
            <div className="product-details">
              <h3 className="product-title">{recommendation.product.name}</h3>
              
              <div className="product-meta">
                <div className="product-brand">{recommendation.product.brand}</div>
                <div className="product-price">${recommendation.product.price.toFixed(2)}</div>
                <div className="product-rating">
                  <span className="rating-value">{recommendation.product.rating}</span>
                  <span className="rating-star">★</span>
                </div>
              </div>
              
              <div className="product-category">
                <a href="#" className="category-link">{recommendation.product.category}</a>
                {recommendation.product.subcategory && (
                  <>
                    <span className="separator">›</span>
                    <a href="#" className="category-link">{recommendation.product.subcategory}</a>
                  </>
                )}
              </div>
              
              <div className="product-tags">
                {recommendation.product.tags && recommendation.product.tags.map((tag, idx) => (
                  <span key={idx} className="tag">{tag}</span>
                ))}
              </div>
            </div>
            
            <div className="recommendation-reason">
              <h4>Why we recommend this:</h4>
              <p>{recommendation.explanation}</p>
              
              <div className="match-score">
                <label>Match score:</label>
                <div className="score-visualization">
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${Math.round(recommendation.relevance_score * 100)}%` }}
                    ></div>
                  </div>
                  <div className="score-value">{Math.round(recommendation.relevance_score * 100)}%</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Recommendations;
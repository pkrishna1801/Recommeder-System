import React from 'react';
import '../styles/App.css';

const Recommendations = ({ recommendations, isLoading }) => {
  if (isLoading) {
    return (
      <div className="recommendations-container loading">
        <div className="loading-spinner"></div>
        <p className="loading-text">Analyzing your preferences and finding the perfect products for you...</p>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="recommendations-container empty">
        <div className="empty-recommendations">
          <h3>No recommendations yet</h3>
          <p>Set your preferences and browse some products, then click "Get Personalized Recommendations"!</p>
          <div className="empty-illustration">
            <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="60" cy="60" r="58" stroke="#e9ecef" strokeWidth="4"/>
              <path d="M40 50C40 44.4772 44.4772 40 50 40H70C75.5228 40 80 44.4772 80 50V70C80 75.5228 75.5228 80 70 80H50C44.4772 80 40 75.5228 40 70V50Z" stroke="#6c757d" strokeWidth="2"/>
              <path d="M60 45V75M45 60H75" stroke="#6c757d" strokeWidth="2"/>
            </svg>
          </div>
          <p className="empty-hint">AI-powered recommendations will appear here based on your preferences and browsing history.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-intro">
        <p>Based on your preferences and browsing history, we think you'll love these products:</p>
      </div>
      
      <div className="recommendations-list">
        {recommendations.map((recommendation, index) => (
          <div key={recommendation.product.id} className="recommendation-card">
            <div className="recommendation-rank">#{index + 1}</div>
            <div className="recommendation-content">
              <div className="recommendation-product-info">
                <h3>{recommendation.product.name}</h3>
                <p className="product-brand">{recommendation.product.brand}</p>
                <p className="product-price">${recommendation.product.price.toFixed(2)}</p>
                <div className="product-rating">Rating: {recommendation.product.rating} ★</div>
                <div className="product-category">
                  {recommendation.product.category} &gt; {recommendation.product.subcategory}
                </div>
                <div className="product-tags">
                  {recommendation.product.tags && recommendation.product.tags.map((tag, idx) => (
                    <span key={idx} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
              <div className="recommendation-explanation">
                <h4>Why we recommend this:</h4>
                <p>{recommendation.explanation}</p>
                <div className="recommendation-score">
                  <span className="score-label">Match score:</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${Math.round(recommendation.relevance_score * 100)}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{Math.round(recommendation.relevance_score * 100)}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="recommendations-footer">
        <p className="recommendations-note">
          These recommendations are powered by AI and will improve as you browse more products and update your preferences.
        </p>
      </div>
    </div>
  );
};

export default Recommendations;
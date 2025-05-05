import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { saveUserPreferences } from '../services/api';
import '../styles/UserProfile.css';

const UserProfile = () => {
  const { user, token, logout, preferences, updatePreferences } = useAuth();
  const [showProfileDetails, setShowProfileDetails] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Handle saving preferences
  const handleSavePreferences = async () => {
    if (!token) return;
    
    setIsSaving(true);
    setSaveMessage('');
    
    try {
      const result = await saveUserPreferences(preferences, token);
      if (result.success) {
        setSaveMessage('Preferences saved successfully!');
        // Update local preferences with saved values
        updatePreferences(result.preferences);
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          setSaveMessage('');
        }, 3000);
      } else {
        setSaveMessage(`Error: ${result.error || 'Failed to save preferences'}`);
      }
    } catch (err) {
      setSaveMessage('Error saving preferences. Please try again.');
      console.error('Error saving preferences:', err);
    } finally {
      setIsSaving(false);
    }
  };

  // Toggle profile details
  const toggleProfileDetails = () => {
    setShowProfileDetails(!showProfileDetails);
  };

  if (!user) {
    return null;
  }

  return (
    <div className="user-profile">
      <div className="user-profile-header">
        <div className="user-info">
          <span className="user-greeting">Welcome, {user.username}!</span>
          <div className="user-actions">
            <button 
              className="profile-toggle-btn"
              onClick={toggleProfileDetails}
            >
              {showProfileDetails ? 'Hide Profile' : 'View Profile'}
            </button>
            <button className="logout-btn" onClick={logout}>
              Logout
            </button>
          </div>
        </div>
      </div>
      
      {showProfileDetails && (
        <div className="profile-details">
          <div className="profile-section">
            <h3>Account Details</h3>
            <div className="profile-info">
              <div className="info-item">
                <span className="info-label">Username:</span>
                <span className="info-value">{user.username}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Email:</span>
                <span className="info-value">{user.email}</span>
              </div>
            </div>
          </div>
          
          <div className="profile-section">
            <h3>Saved Preferences</h3>
            <div className="preferences-summary">
              {preferences.category_preferences && preferences.category_preferences.length > 0 ? (
                <div className="info-item">
                  <span className="info-label">Categories:</span>
                  <span className="info-value">{preferences.category_preferences.join(', ')}</span>
                </div>
              ) : (
                <div className="info-item">
                  <span className="info-label">Categories:</span>
                  <span className="info-value info-empty">No categories selected</span>
                </div>
              )}
              
              {preferences.brand_preferences && preferences.brand_preferences.length > 0 ? (
                <div className="info-item">
                  <span className="info-label">Brands:</span>
                  <span className="info-value">{preferences.brand_preferences.join(', ')}</span>
                </div>
              ) : (
                <div className="info-item">
                  <span className="info-label">Brands:</span>
                  <span className="info-value info-empty">No brands selected</span>
                </div>
              )}
              
              <div className="info-item">
                <span className="info-label">Price Range:</span>
                <span className="info-value">
                  {preferences.price_range && (preferences.price_range.min || preferences.price_range.max) ? (
                    `$${preferences.price_range.min || 0} - ${preferences.price_range.max ? `$${preferences.price_range.max}` : 'Any'}`
                  ) : (
                    <span className="info-empty">No price range set</span>
                  )}
                </span>
              </div>
            </div>
            
            <div className="preferences-actions">
              <button 
                className="save-preferences-btn"
                onClick={handleSavePreferences}
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : 'Save Current Preferences'}
              </button>
              {saveMessage && (
                <div className={`save-message ${saveMessage.includes('Error') ? 'error' : 'success'}`}>
                  {saveMessage}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
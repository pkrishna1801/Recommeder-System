import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css';
import './styles/Auth.css';
import './styles/UserProfile.css';
import './styles/UserPreferences.css';
import './styles/BrowsingHistory.css';
import './styles/Recommendations.css'; // Add this line for the new recommendations styles
import './styles/additional-styles.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
import React from 'react';
import ReactDOM from 'react-dom/client';
import './styles/App.css';
import './styles/Auth.css';
import './styles/UserProfile.css';
import './styles/UserPreferences.css';
import './styles/BrowsingHistory.css';
import './styles/additional-styles.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';
import '../styles/Auth.css';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  const toggleForm = () => {
    setIsLogin(!isLogin);
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-logo">
          <h1>AI Product Recommendations</h1>
          <p>Find the perfect products tailored to your preferences</p>
        </div>
        
        {isLogin ? (
          <Login onToggleForm={toggleForm} />
        ) : (
          <Register onToggleForm={toggleForm} />
        )}
      </div>
    </div>
  );
};

export default AuthPage;
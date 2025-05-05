import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import '../styles/Auth.css';

const Login = ({ onToggleForm }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');

  const { login, loading, error } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');

    // Validate inputs
    if (!username.trim()) {
      setFormError('Username is required');
      return;
    }

    if (!password.trim()) {
      setFormError('Password is required');
      return;
    }

    // Attempt login
    const result = await login(username, password);

    // Display form-specific errors
    if (!result.success) {
      setFormError(result.error || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="auth-form-container">
      <h2>Login</h2>
      
      {formError && <div className="auth-error">{formError}</div>}
      {error && !formError && <div className="auth-error">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
          />
        </div>
        
        <button 
          type="submit" 
          className="auth-button"
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <div className="auth-toggle">
        Don't have an account?{' '}
        <button 
          className="auth-toggle-button" 
          onClick={onToggleForm}
          disabled={loading}
        >
          Register
        </button>
      </div>
    </div>
  );
};

export default Login;
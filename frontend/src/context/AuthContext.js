import React, { createContext, useState, useEffect, useContext } from 'react';
import { 
  registerUser, 
  loginUser, 
  verifyToken, 
  getUserProfile, 
  getUserPreferences 
} from '../services/api';

// Create the auth context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  // State for authentication
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [preferences, setPreferences] = useState({
    category_preferences: [],
    price_range: { min: null, max: null },
    brand_preferences: []
  });

  // Check if token is valid on initial load
  useEffect(() => {
    const checkAuth = async () => {
      if (token) {
        try {
          const response = await verifyToken(token);
          if (response.success) {
            setUser(response.user);
            
            // Load user preferences
            const prefsResponse = await getUserPreferences(token);
            if (prefsResponse.success) {
              setPreferences(prefsResponse.preferences);
            }
          } else {
            // Token invalid, clear it
            setToken(null);
            localStorage.removeItem('token');
          }
        } catch (err) {
          console.error('Authentication error:', err);
          setToken(null);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, [token]);

  // Register function
  const register = async (username, email, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await registerUser(username, email, password);
      if (response.success) {
        setUser(response.user);
        setToken(response.token);
        localStorage.setItem('token', response.token);
        
        // Set initial preferences if available
        if (response.user.preferences) {
          setPreferences(response.user.preferences);
        }
      } else {
        setError(response.error || 'Registration failed');
      }
      setLoading(false);
      return response;
    } catch (err) {
      setError(err.message || 'Registration failed');
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  // Login function
  const login = async (username, password) => {
    setLoading(true);
    setError(null);
    try {
      const response = await loginUser(username, password);
      if (response.success) {
        setUser(response.user);
        setToken(response.token);
        localStorage.setItem('token', response.token);
        
        // Set preferences if available
        if (response.user.preferences) {
          setPreferences(response.user.preferences);
        }
      } else {
        setError(response.error || 'Login failed');
      }
      setLoading(false);
      return response;
    } catch (err) {
      setError(err.message || 'Login failed');
      setLoading(false);
      return { success: false, error: err.message };
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setToken(null);
    setPreferences({
      category_preferences: [],
      price_range: { min: null, max: null },
      brand_preferences: []
    });
    localStorage.removeItem('token');
  };

  // Update preferences
  const updatePreferences = (newPreferences) => {
    setPreferences(prevPreferences => ({
      ...prevPreferences,
      ...newPreferences
    }));
  };

  // Context value
  const value = {
    user,
    token,
    loading,
    error,
    preferences,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updatePreferences
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
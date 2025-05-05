const API_BASE_URL = 'http://localhost:5000/api';

// Helper function to prepare headers with auth token if available
const getHeaders = (token = null) => {
  const headers = {
    'Content-Type': 'application/json'
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  return headers;
};

// Authentication methods
export const registerUser = async (username, email, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, email, password })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const verifyToken = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/verify`, {
      method: 'GET',
      headers: getHeaders(token)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Token verification error:', error);
    throw error;
  }
};

// User profile and preferences
export const getUserProfile = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/profile`, {
      method: 'GET',
      headers: getHeaders(token)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

export const getUserPreferences = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/preferences`, {
      method: 'GET',
      headers: getHeaders(token)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user preferences:', error);
    throw error;
  }
};

export const saveUserPreferences = async (preferences, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/preferences`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(preferences)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error saving user preferences:', error);
    throw error;
  }
};

// Browsing history
export const getUserBrowsingHistory = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/browsing-history`, {
      method: 'GET',
      headers: getHeaders(token)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching browsing history:', error);
    throw error;
  }
};

export const addToBrowsingHistory = async (productId, token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/browsing-history`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify({ product_id: productId })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error adding to browsing history:', error);
    throw error;
  }
};

export const clearBrowsingHistory = async (token) => {
  try {
    const response = await fetch(`${API_BASE_URL}/user/browsing-history`, {
      method: 'DELETE',
      headers: getHeaders(token)
    });
    
    return await response.json();
  } catch (error) {
    console.error('Error clearing browsing history:', error);
    throw error;
  }
};

// Product catalog
export const fetchProducts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

export const fetchProductCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/categories`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

export const fetchProductBrands = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/brands`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching brands:', error);
    throw error;
  }
};

export const fetchPriceRange = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/price-range`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching price range:', error);
    throw error;
  }
};

// Recommendations
export const getRecommendations = async (preferences, browsingHistory, token = null) => {
  try {
    // Convert preferences to the format expected by the backend
    const requestData = {
      preferences: {
        category_preferences: preferences.category_preferences || [],
        price_range: preferences.price_range || { min: null, max: null },
        brand_preferences: preferences.brand_preferences || []
      },
      browsing_history: browsingHistory
    };

    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: getHeaders(token),
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};
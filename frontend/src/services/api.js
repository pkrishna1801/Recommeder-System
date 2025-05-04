const API_BASE_URL = 'http://localhost:5000/api';

/**
 * Fetch all products from the API
 * @returns {Promise<Array>} A promise that resolves to an array of products
 */
export const fetchProducts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch products');
    }
    
    return data.products;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

/**
 * Fetch all available categories from the API
 * @returns {Promise<Array>} A promise that resolves to an array of category names
 */
export const fetchCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/categories`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch categories');
    }
    
    return data.categories;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

/**
 * Fetch all available brands from the API
 * @returns {Promise<Array>} A promise that resolves to an array of brand names
 */
export const fetchBrands = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/brands`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch brands');
    }
    
    return data.brands;
  } catch (error) {
    console.error('Error fetching brands:', error);
    throw error;
  }
};

/**
 * Get a single product by ID
 * @param {string} productId - The ID of the product to fetch
 * @returns {Promise<Object>} A promise that resolves to a product object
 */
export const getProductById = async (productId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch product');
    }
    
    return data.product;
  } catch (error) {
    console.error(`Error fetching product ${productId}:`, error);
    throw error;
  }
};

/**
 * Get recommendations based on user preferences and browsing history
 * @param {Object} preferences - User preferences object
 * @param {Array} browsingHistory - Array of product IDs the user has viewed
 * @returns {Promise<Array>} A promise that resolves to an array of recommendations
 */
export const getRecommendations = async (preferences, browsingHistory) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        preferences: preferences,
        browsing_history: browsingHistory
      }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Failed to get recommendations');
    }
    
    return data.recommendations;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};
import numpy as np
import openai
import json
import os
from functools import lru_cache
from config import config

# Try to import FAISS 
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Falling back to NumPy for similarity search.")


class EmbeddingService:
    """
    Service to handle embeddings for products and user data
    Supports semantic similarity search for more accurate recommendations
    """
    
    def __init__(self):
        """Initialize the embedding service with configuration"""
        openai.api_key = config.get('OPENAI_API_KEY')
        self.embedding_model = config.get('EMBEDDING_MODEL', 'text-embedding-ada-002')
        self.embedding_dim = config.get('EMBEDDING_DIM', 1536)  # Dimension of embeddings
        self.cache_dir = config.get('CACHE_DIR', 'cache')
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        # Initialize storage for product embeddings
        self.product_embeddings = {}
        self.product_index = None
        self.product_ids = []
    
    def get_embedding(self, text):
        """
        Get embedding for a text string using OpenAI's API
        Uses caching to avoid redundant API calls
        """
        # Normalize text for consistent embedding
        text = text.strip().lower()
        
        # Generate a cache key (simple hash of the text)
        cache_key = str(hash(text))
        cache_path = os.path.join(self.cache_dir, f"emb_{cache_key}.json")
        
        # Check if we have this embedding cached
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    return np.array(json.load(f))
            except (json.JSONDecodeError, IOError):
                # If there's an issue with the cache file, proceed to generate a new embedding
                pass
        
        try:
            # Get embedding from OpenAI API
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response["data"][0]["embedding"]
            
            # Cache the embedding
            with open(cache_path, 'w') as f:
                json.dump(embedding, f)
            
            return np.array(embedding)
            
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            # Return a zero vector as fallback
            return np.zeros(self.embedding_dim)
    
    def get_product_embedding(self, product):
        """
        Get embedding for a product by combining its relevant attributes
        """
        # Extract relevant product information
        product_info = [
            f"Name: {product.get('name', '')}",
            f"Category: {product.get('category', '')}, Subcategory: {product.get('subcategory', '')}",
            f"Brand: {product.get('brand', '')}, Price: {product.get('price', 0)}",
            f"Description: {product.get('description', '')}"
        ]
        
        # Add features if available
        if 'features' in product and product['features']:
            product_info.append(f"Features: {', '.join(product['features'])}")
        
        # Add tags if available
        if 'tags' in product and product['tags']:
            product_info.append(f"Tags: {', '.join(product['tags'])}")
        
        # Combine all product information into a single text
        product_text = " ".join(product_info)
        
        # Get embedding for the product text
        return self.get_embedding(product_text)
    
    def embed_all_products(self, products):
        """
        Create embeddings for all products and build a search index
        """
        # Skip if no products
        if not products:
            return
        
        # Reset storage
        self.product_embeddings = {}
        self.product_ids = []
        
        # Generate embeddings for all products
        embeddings = []
        for product in products:
            product_id = product['id']
            self.product_ids.append(product_id)
            
            # Get embedding
            embedding = self.get_product_embedding(product)
            
            # Store in dictionary
            self.product_embeddings[product_id] = embedding
            
            # Add to list for index building
            embeddings.append(embedding)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Build search index
        if FAISS_AVAILABLE:
            # Use FAISS for efficient similarity search
            self.product_index = faiss.IndexFlatL2(self.embedding_dim)
            self.product_index.add(embeddings_array)
        else:
            # Just store the embeddings as numpy array
            self.product_index = embeddings_array
    
    def get_user_interests_embedding(self, browsed_products, user_preferences):
        """
        Generate an embedding representing the user's interests
        based on browsing history and explicit preferences
        """
        if not browsed_products:
            # If no browsing history, create an embedding from preferences
            return self._get_preferences_embedding(user_preferences)
        
        # Combine browsing history embeddings with preference embedding
        history_embedding = self._get_history_embedding(browsed_products)
        
        if not user_preferences:
            # If no preferences, just use browsing history
            return history_embedding
        
        # Get preferences embedding
        preferences_embedding = self._get_preferences_embedding(user_preferences)
        
        # Combine with 70% weight on browsing history, 30% on preferences
        combined_embedding = 0.7 * history_embedding + 0.3 * preferences_embedding
        
        # Normalize the embedding
        norm = np.linalg.norm(combined_embedding)
        if norm > 0:
            combined_embedding = combined_embedding / norm
        
        return combined_embedding
    
    def _get_history_embedding(self, browsed_products):
        """
        Create an embedding representing the user's browsing history
        """
        # If no browsing history, return zero vector
        if not browsed_products:
            return np.zeros(self.embedding_dim)
        
        # Get embeddings for all browsed products
        embeddings = []
        for product in browsed_products:
            # Get embedding
            embedding = self.get_product_embedding(product)
            embeddings.append(embedding)
        
        # Weight more recent products higher (if products are in chronological order)
        weights = np.linspace(0.5, 1.0, len(embeddings))
        
        # Compute weighted average embedding
        weighted_embedding = np.zeros(self.embedding_dim)
        for i, embedding in enumerate(embeddings):
            weighted_embedding += weights[i] * embedding
        
        # Normalize the embedding
        norm = np.linalg.norm(weighted_embedding)
        if norm > 0:
            weighted_embedding = weighted_embedding / norm
        
        return weighted_embedding
    
    def _get_preferences_embedding(self, user_preferences):
        """
        Create an embedding representing the user's explicit preferences
        """
        # Extract preference info
        preference_texts = []
        
        for key, value in user_preferences.items():
            if value:
                # Handle different types of preference values
                if isinstance(value, dict):
                    # Handle nested dictionaries like price range
                    for sub_key, sub_value in value.items():
                        if sub_value is not None:
                            preference_texts.append(f"{key.replace('_', ' ')} {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    # Handle lists like category preferences
                    preference_texts.append(f"{key.replace('_', ' ')}: {', '.join(value)}")
                else:
                    # Handle simple values
                    preference_texts.append(f"{key.replace('_', ' ')}: {value}")
        
        # If no preferences, return zero vector
        if not preference_texts:
            return np.zeros(self.embedding_dim)
        
        # Combine preferences into a single text
        preferences_text = " User prefers " + ". ".join(preference_texts)
        
        # Get embedding for the preferences text
        return self.get_embedding(preferences_text)
    
    def find_similar_products(self, query_embedding, products, top_n=5, exclude_ids=None):
        """
        Find the most similar products to a query embedding
        
        Parameters:
        - query_embedding: The embedding to compare against
        - products: List of products to search
        - top_n: Number of results to return
        - exclude_ids: Product IDs to exclude from results
        
        Returns:
        - List of tuples (product, similarity_score)
        """
        if exclude_ids is None:
            exclude_ids = []
        
        # Ensure we have the index and embeddings
        if self.product_index is None or not self.product_ids:
            self.embed_all_products(products)
        
        # Normalize the query embedding
        norm = np.linalg.norm(query_embedding)
        if norm > 0:
            query_embedding = query_embedding / norm
        
        # Reshape for FAISS
        query_embedding = np.array([query_embedding]).astype('float32')
        
        if FAISS_AVAILABLE and isinstance(self.product_index, faiss.Index):
            # Use FAISS for efficient similarity search
            distances, indices = self.product_index.search(query_embedding, len(self.product_ids))
            
            # Convert results to product, score tuples
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.product_ids):
                    product_id = self.product_ids[idx]
                    
                    # Skip excluded products
                    if product_id in exclude_ids:
                        continue
                    
                    # Find the product with this ID
                    product = next((p for p in products if p['id'] == product_id), None)
                    
                    if product:
                        # Convert distance to similarity score (1 - normalized distance)
                        score = 1.0 - min(distances[0][i] / 10.0, 1.0)
                        results.append((product, score))
            
        else:
            # Fallback to numpy-based search
            results = []
            for product in products:
                product_id = product['id']
                
                # Skip excluded products
                if product_id in exclude_ids:
                    continue
                
                # Get product embedding
                embedding = self.get_product_embedding(product)
                
                # Normalize the embedding
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding[0], embedding)
                
                results.append((product, similarity))
        
        # Sort by similarity score (highest first) and take top N
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_n]
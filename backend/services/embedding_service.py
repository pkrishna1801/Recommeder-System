import numpy as np
import faiss
import openai  # Using the older style import
from config import config

class EmbeddingService:
    """
    Service to handle product embeddings and similarity searches using FAISS
    """
    
    def __init__(self):
        """Initialize the embedding service"""
        openai.api_key = config['OPENAI_API_KEY']
        self.embedding_model = "text-embedding-ada-002"
        self.embedding_dim = 1536  # Dimension for OpenAI embeddings
        self.product_embeddings = {}  # Cache for product embeddings
        self.product_ids = []  # To keep track of product IDs
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.is_index_trained = False
    
    def _create_product_text(self, product):
        """Create a text representation of a product for embedding"""
        text = f"{product['name']} {product.get('category', '')} {product.get('subcategory', '')} "
        text += f"{product.get('brand', '')} {product.get('description', '')} "
        
        # Add tags
        if 'tags' in product and product['tags']:
            text += " ".join(product['tags'])
            
        # Add features
        if 'features' in product and product['features']:
            text += " " + " ".join(product['features'])
            
        return text
    
    def get_embedding(self, text):
        """Get embedding for a text string"""
        try:
            # Using the older OpenAI API style
            response = openai.Embedding.create(
                model=self.embedding_model,
                input=text
            )
            return np.array(response['data'][0]['embedding'], dtype=np.float32)
        except Exception as e:
            print(f"Error creating embedding: {str(e)}")
            # Return a zero vector as fallback
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def embed_product(self, product):
        """Create an embedding for a product"""
        product_id = product['id']
        
        # Check if embedding is already cached
        if product_id in self.product_embeddings:
            return self.product_embeddings[product_id]
        
        # Create text representation and get embedding
        text = self._create_product_text(product)
        embedding = self.get_embedding(text)
        
        # Cache the embedding
        self.product_embeddings[product_id] = embedding
        
        return embedding
    
    def embed_all_products(self, products):
        """Create embeddings for a list of products and build the FAISS index"""
        # Reset the index and ID mapping
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.product_ids = []
        
        # Generate embeddings for all products
        embeddings = []
        for product in products:
            product_id = product['id']
            embedding = self.embed_product(product)
            embeddings.append(embedding)
            self.product_ids.append(product_id)
        
        # Convert to numpy array and add to index
        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_array)
            self.is_index_trained = True
    
    def find_similar_products(self, query_embedding, products, top_n=10, exclude_ids=None):
        """Find products similar to a query embedding using FAISS"""
        if exclude_ids is None:
            exclude_ids = []
            
        # Make sure index is built
        if not self.is_index_trained or self.index.ntotal == 0:
            self.embed_all_products(products)
        
        # Reshape query vector for FAISS
        query_embedding = query_embedding.reshape(1, -1)
        
        # Perform the search
        distances, indices = self.index.search(query_embedding, top_n + len(exclude_ids))
        
        # Create product ID to product mapping for quick lookup
        product_map = {product['id']: product for product in products}
        
        # Filter and format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.product_ids):
                continue  # Skip invalid indices
                
            product_id = self.product_ids[idx]
            
            # Skip excluded IDs
            if product_id in exclude_ids:
                continue
                
            # Get the product
            if product_id in product_map:
                product = product_map[product_id]
                
                # Convert distance to similarity score
                similarity = 1.0 / (1.0 + distances[0][i])
                
                results.append((product, similarity))
                
                # Break if we have enough results
                if len(results) >= top_n:
                    break
        
        return results

    def get_user_interests_embedding(self, browsed_products, user_preferences=None):
        """Create an embedding representing user interests"""
        # Combine browsed product descriptions
        texts = [self._create_product_text(product) for product in browsed_products]
        
        # Add preference information if available
        if user_preferences:
            preference_text = ""
            for key, value in user_preferences.items():
                if value:
                    preference_text += f"{key} {value} "
            
            if preference_text:
                texts.append(preference_text)
        
        # Combine texts
        combined_text = " ".join(texts)
        
        # Get embedding
        return self.get_embedding(combined_text)
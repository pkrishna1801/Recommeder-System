# services/llm_service.py
import openai
import json
import re
from config import config
# from services.embedding_service import EmbeddingService

# Add to your imports
from services.embedding_service import EmbeddingService

class LLMService:
    
    def __init__(self):
        """Initialize the LLM service with configuration"""
        openai.api_key = config['OPENAI_API_KEY']
        self.model_name = config['MODEL_NAME']
        self.max_tokens = config['MAX_TOKENS']
        self.temperature = config['TEMPERATURE']
        self.embedding_service = EmbeddingService()  # Initialize embedding service
    
    def generate_recommendations(self, user_preferences, browsing_history, all_products):
        """Generate personalized product recommendations"""
        # Get browsed products details
        browsed_products = []
        for product_id in browsing_history:
            for product in all_products:
                if product["id"] == product_id:
                    browsed_products.append(product)
                    break
        
        # If we have no browsing history, use a basic approach
        if not browsed_products:
            # Pre-filter products to reduce token usage
            relevant_products = self._prefilter_products(user_preferences, browsed_products, all_products)
            prompt = self._create_recommendation_prompt(user_preferences, browsed_products, relevant_products)
        else:
            # Use RAG approach for more efficient token usage
            relevant_products = self._rag_find_relevant_products(user_preferences, browsed_products, all_products)
            prompt = self._create_rag_prompt(user_preferences, browsed_products, relevant_products)
        
        # Call the LLM API
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert eCommerce product recommendation system."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the LLM response to extract recommendations
            recommendations = self._parse_recommendation_response(response.choices[0].message.content, all_products)
            
            return recommendations
            
        except Exception as e:
            print(f"Error calling LLM API: {str(e)}")
            raise Exception(f"Failed to generate recommendations: {str(e)}")
    
    def _rag_find_relevant_products(self, user_preferences, browsed_products, all_products, max_products=10):
        """Use RAG approach with FAISS to find relevant products"""
        # First apply basic filtering if preferences exist
        filtered_products = all_products.copy()
        
        # Filter by category if specified
        if 'category' in user_preferences and user_preferences['category']:
            categories = user_preferences['category']
            if isinstance(categories, str):
                categories = [categories]
            filtered_products = [p for p in filtered_products if p.get('category') in categories]
        
        # Filter by price range if specified
        if 'price_range' in user_preferences:
            price_range = user_preferences['price_range']
            if 'min' in price_range and price_range['min'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) >= price_range['min']]
            if 'max' in price_range and price_range['max'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) <= price_range['max']]
        
        # Now do embedding-based similarity search
        if browsed_products:
            # Ensure FAISS index is built with the filtered products
            self.embedding_service.embed_all_products(filtered_products)
            
            # Get embedding for user interests
            user_embedding = self.embedding_service.get_user_interests_embedding(
                browsed_products, user_preferences
            )
            
            # Get IDs of products already browsed to exclude them
            browsed_ids = [p['id'] for p in browsed_products]
            
            # Find similar products using FAISS
            similar_products = self.embedding_service.find_similar_products(
                user_embedding, 
                filtered_products,
                top_n=max_products,
                exclude_ids=browsed_ids
            )
            
            # Extract just the products (without scores)
            relevant_products = [p[0] for p in similar_products]
        else:
            # If no browsing history, just use the filtered products
            relevant_products = filtered_products[:max_products]
        
        return relevant_products
    
    def _create_rag_prompt(self, user_preferences, browsed_products, relevant_products):
        """Create a compact and efficient prompt for the LLM using RAG results"""
        # Create a much more compact prompt
        prompt = """
        You are an expert e-commerce product recommendation specialist. Your task is to recommend the most relevant products for a user based on their browsing history and preferences.

        # USER BROWSING HISTORY
        """
        
        # Add browsing history in compact format
        if browsed_products:
            for product in browsed_products:
                prompt += f"- {product['name']} (ID: {product['id']})\n"
                prompt += f"  Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
                prompt += f"  Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}\n"
                if 'tags' in product and product['tags']:
                    prompt += f"  Tags: {', '.join(product['tags'])}\n"
                prompt += "\n"
        else:
            prompt += "- No browsing history available\n"
        
        # Add user preferences in compact format
        prompt += "\n# USER PREFERENCES\n"
        if user_preferences:
            for key, value in user_preferences.items():
                if value:
                    prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            prompt += "- No explicit preferences provided\n"
        
        # Add available products section - much more compact
        prompt += "\n# AVAILABLE PRODUCTS FOR RECOMMENDATION\n"
        
        for i, product in enumerate(relevant_products):
            prompt += f"Product {i+1}: {product['name']} (ID: {product['id']})\n"
            prompt += f"- Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
            prompt += f"- Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}\n"
            prompt += f"- Rating: {product.get('rating', 'N/A')}\n"
            
            # Add a compact description
            description = product.get('description', '')
            if len(description) > 100:
                description = description[:97] + "..."
            prompt += f"- Description: {description}\n"
            
            # Add key features (limited to 3)
            if 'features' in product and product['features']:
                prompt += f"- Features: {', '.join(product['features'][:3])}\n"
            
            # Add key tags
            if 'tags' in product and product['tags']:
                prompt += f"- Tags: {', '.join(product['tags'])}\n"
            
            prompt += "\n"
        
        # Add task instructions - keep them clear but concise
        prompt += """
        # TASK
        Based on the user's browsing history and preferences, recommend 5 products from the available products list.

        IMPORTANT INSTRUCTIONS:
        1. Make COHERENT recommendations - products should be logically related to what the user has browsed
        2. Provide a UNIQUE and SPECIFIC explanation for each product explaining exactly why it matches this user's interests
        3. Make sure your explanations match the actual product being recommended - don't reference features the product doesn't have
        4. Ensure you don't recommend duplicate products
        5. Assign a relevance score (0-100) to each product based on how well it matches the user's interests

        # OUTPUT FORMAT
        Return your recommendations as a valid JSON array of objects with the following structure:
        [
          {
            "product_id": "product123",
            "relevance_score": 95,
            "explanation": "Detailed explanation of why this specific product matches the user's preferences and browsing patterns"
          },
          ...
        ]

        Ensure your output is valid, parseable JSON with exactly these three fields for each recommendation.
        """
        
        return prompt
    
    # Keep existing methods for backward compatibility 
    # (unchanged - _prefilter_products, _create_recommendation_prompt, _parse_recommendation_response)
    def _prefilter_products(self, user_preferences, browsed_products, all_products, max_products=10):
        """
        Pre-filter products based on user preferences and find semantically similar products using embeddings
        
        Parameters:
        - user_preferences (dict): User's stated preferences
        - browsed_products (list): Products the user has viewed
        - all_products (list): Full product catalog
        - max_products (int): Maximum number of products to include
        
        Returns:
        - list: Filtered list of relevant products
        """
        # Start with basic filtering based on preferences
        filtered_products = all_products.copy()
        
        # Filter by category if specified
        if 'category' in user_preferences and user_preferences['category']:
            categories = user_preferences['category']
            if isinstance(categories, str):
                categories = [categories]
            filtered_products = [p for p in filtered_products if p.get('category') in categories]
        
        # Filter by price range if specified
        if 'price_range' in user_preferences:
            price_range = user_preferences['price_range']
            if 'min' in price_range and price_range['min'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) >= price_range['min']]
            if 'max' in price_range and price_range['max'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) <= price_range['max']]
        
        # Filter by brand if specified
        if 'brand' in user_preferences and user_preferences['brand']:
            brands = user_preferences['brand']
            if isinstance(brands, str):
                brands = [brands]
            filtered_products = [p for p in filtered_products if p.get('brand') in brands]
        
        # If we have browsing history, use embeddings to find similar products
        if browsed_products:
            # Get IDs of products already browsed
            browsed_ids = [p['id'] for p in browsed_products]
            
            # Get embedding for user interests
            user_embedding = self._get_user_interests_embedding(browsed_products, user_preferences)
            
            # Find similar products
            similar_products = self._find_similar_products(
                user_embedding, 
                filtered_products, 
                top_n=max_products,
                exclude_ids=browsed_ids
            )
            
            # Extract just the products (without scores)
            filtered_products = [p[0] for p in similar_products]
        
        # Limit to max_products
        return filtered_products[:max_products]
    
    def _create_recommendation_prompt(self, user_preferences, browsed_products, relevant_products):
        """
        Create an improved prompt for getting better recommendations
        """
        prompt = """
        You are an expert e-commerce product recommendation specialist. Your task is to recommend the most relevant products for a user based on their browsing history and preferences.
        
        # USER BROWSING HISTORY
        """
        
        # Add browsing history details
        if browsed_products:
            for product in browsed_products:
                prompt += f"- {product['name']} (ID: {product['id']})\n"
                prompt += f"  Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
                prompt += f"  Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}\n"
                
                if 'tags' in product and product['tags']:
                    prompt += f"  Tags: {', '.join(product['tags'])}\n"
                
                prompt += "\n"
        else:
            prompt += "No browsing history available.\n\n"
        
        # Add user preferences
        prompt += "# USER PREFERENCES\n"
        if user_preferences:
            for key, value in user_preferences.items():
                if value:
                    prompt += f"- {key.replace('_', ' ').title()}: {value}\n"
        else:
            prompt += "No specific preferences provided.\n"
        
        prompt += "\n# AVAILABLE PRODUCTS FOR RECOMMENDATION\n\n"
        
        # Add available products with detailed information
        for i, product in enumerate(relevant_products):
            prompt += f"Product {i+1}: {product['name']} (ID: {product['id']})\n"
            prompt += f"- Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
            prompt += f"- Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}\n"
            
            if 'rating' in product:
                prompt += f"- Rating: {product['rating']}\n"
            
            if 'description' in product:
                prompt += f"- Description: {product['description']}\n"
            
            if 'features' in product and product['features']:
                prompt += f"- Features: {', '.join(product['features'][:3])}\n"
            
            if 'tags' in product and product['tags']:
                prompt += f"- Tags: {', '.join(product['tags'])}\n"
            
            prompt += "\n"
        
        # Add detailed instructions for the recommendations
        prompt += """
        # TASK
        Based on the user's browsing history and preferences, recommend 5 products from the available products list.
        
        IMPORTANT INSTRUCTIONS:
        1. Make COHERENT recommendations - products should be logically related to what the user has browsed
        2. Provide a UNIQUE and SPECIFIC explanation for each product explaining exactly why it matches this user's interests
        3. Make sure your explanations match the actual product being recommended - don't reference features the product doesn't have
        4. Ensure you don't recommend duplicate products
        5. Assign a relevance score (0-100) to each product based on how well it matches the user's interests
        
        # OUTPUT FORMAT
        Return your recommendations as a valid JSON array of objects with the following structure:
        [
        {
            "product_id": "product123",
            "relevance_score": 95,
            "explanation": "Detailed explanation of why this specific product matches the user's preferences and browsing patterns"
        },
        ...
        ]
        
        Ensure your output is valid, parseable JSON with exactly these three fields for each recommendation.
        """
        print(f"Generated prompt for LLM:\n{prompt}")
        return prompt
    
    def _parse_recommendation_response(self, llm_response, all_products):
        """
        Parse the LLM response to extract product recommendations
        
        Parameters:
        - llm_response (str): Raw response from the LLM
        - all_products (list): Full product catalog to match IDs with full product info
        
        Returns:
        - dict: Structured recommendations
        """
        try:
            # Find JSON content in the response using regex
            json_pattern = r'\[\s*{.*}\s*\]'
            match = re.search(json_pattern, llm_response, re.DOTALL)
            
            if match:
                json_str = match.group(0)
            else:
                # Try another approach - look for array brackets
                start_idx = llm_response.find('[')
                end_idx = llm_response.rfind(']') + 1
                
                if start_idx == -1 or end_idx <= 0:
                    return {
                        "recommendations": [],
                        "error": "Could not parse recommendations from LLM response"
                    }
                
                json_str = llm_response[start_idx:end_idx]
            
            # Clean up the JSON string to handle common formatting issues
            # Remove any markdown code block markers
            json_str = re.sub(r'```json|```', '', json_str)
            
            # Parse the JSON
            rec_data = json.loads(json_str)
            
            # Create a lookup dictionary for faster product matching
            product_lookup = {product['id']: product for product in all_products}
            
            # Enrich recommendations with full product details
            recommendations = []
            for rec in rec_data:
                product_id = rec.get('product_id')
                
                # Find the product in the lookup dictionary
                product_details = product_lookup.get(product_id)
                
                if product_details:
                    # Validate and normalize the relevance score
                    relevance_score = rec.get('relevance_score', 0.5)
                    if isinstance(relevance_score, str):
                        try:
                            relevance_score = float(relevance_score)
                        except ValueError:
                            relevance_score = 0.5
                    
                    # Ensure score is between 0 and 1
                    relevance_score = max(0, min(1, relevance_score))
                    
                    recommendations.append({
                        "product": product_details,
                        "explanation": rec.get('explanation', ''),
                        "relevance_score": relevance_score
                    })
            
            # Sort recommendations by relevance score (highest first)
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return {
                "recommendations": recommendations,
                "count": len(recommendations)
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            print(f"Problematic JSON string: {json_str}")
            return {
                "recommendations": [],
                "error": f"Failed to parse JSON from LLM response: {str(e)}"
            }
        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            return {
                "recommendations": [],
                "error": f"Failed to parse recommendations: {str(e)}"
            }
        
    def _rag_find_relevant_products(self, user_preferences, browsed_products, all_products, max_products=10):
        """
        Use RAG approach with FAISS to find relevant products based on embeddings
        
        Parameters:
        - user_preferences (dict): User's stated preferences
        - browsed_products (list): Products the user has viewed
        - all_products (list): Full product catalog
        - max_products (int): Maximum number of products to include
        
        Returns:
        - list: Filtered list of relevant products
        """
        # First apply basic filtering if preferences exist
        filtered_products = all_products.copy()
        
        # Filter by category if specified
        if 'category' in user_preferences and user_preferences['category']:
            categories = user_preferences['category']
            if isinstance(categories, str):
                categories = [categories]
            filtered_products = [p for p in filtered_products if p.get('category') in categories]
        
        # Filter by price range if specified
        if 'price_range' in user_preferences:
            price_range = user_preferences['price_range']
            if 'min' in price_range and price_range['min'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) >= price_range['min']]
            if 'max' in price_range and price_range['max'] is not None:
                filtered_products = [p for p in filtered_products if p.get('price', 0) <= price_range['max']]
        
        # Now we do embedding-based similarity search
        if browsed_products:
            # Ensure FAISS index is built with the filtered products
            self.embedding_service.embed_all_products(filtered_products)
            
            # Get embedding for user interests
            user_embedding = self.embedding_service.get_user_interests_embedding(
                browsed_products, user_preferences
            )
            
            # Get IDs of products already browsed to exclude them
            browsed_ids = [p['id'] for p in browsed_products]
            
            # Find similar products using FAISS
            similar_products = self.embedding_service.find_similar_products(
                user_embedding, 
                filtered_products,
                top_n=max_products,
                exclude_ids=browsed_ids
            )
            
            # Extract just the products (without scores)
            relevant_products = [p[0] for p in similar_products]
        else:
            # If no browsing history, just use the filtered products
            relevant_products = filtered_products[:max_products]
        
        return relevant_products
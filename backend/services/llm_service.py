import openai
import json
import re
from config import config

class LLMService:
    """
    Service to handle interactions with the LLM API
    """
    
    def __init__(self):
        """
        Initialize the LLM service with configuration
        """
        openai.api_key = config['OPENAI_API_KEY']
        self.model_name = config['MODEL_NAME']
        self.max_tokens = config['MAX_TOKENS']
        self.temperature = config['TEMPERATURE']
    
    def generate_recommendations(self, user_preferences, browsing_history, all_products):
        """
        Generate personalized product recommendations based on user preferences and browsing history
        
        Parameters:
        - user_preferences (dict): User's stated preferences
        - browsing_history (list): List of product IDs the user has viewed
        - all_products (list): Full product catalog
        
        Returns:
        - dict: Recommended products with explanations
        """
        # Get browsed products details
        browsed_products = []
        for product_id in browsing_history:
            for product in all_products:
                if product["id"] == product_id:
                    browsed_products.append(product)
                    break
        
        # Pre-filter products to reduce token usage
        relevant_products = self._prefilter_products(user_preferences, browsed_products, all_products)
        
        # Create a prompt for the LLM
        prompt = self._create_recommendation_prompt(user_preferences, browsed_products, relevant_products)
        
        # Call the LLM API
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert eCommerce product recommendation system. Your recommendations are personalized, insightful, and based on a deep understanding of product features and customer preferences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse the LLM response to extract recommendations
            recommendations = self._parse_recommendation_response(response.choices[0].message.content, all_products)
            
            return recommendations
            
        except Exception as e:
            # Handle any errors from the LLM API
            print(f"Error calling LLM API: {str(e)}")
            raise Exception(f"Failed to generate recommendations: {str(e)}")
    
    def _prefilter_products(self, user_preferences, browsed_products, all_products, max_products=30):
        """
        Pre-filter products based on user preferences to reduce token usage
        
        Parameters:
        - user_preferences (dict): User's stated preferences
        - browsed_products (list): Products the user has viewed
        - all_products (list): Full product catalog
        - max_products (int): Maximum number of products to include
        
        Returns:
        - list: Filtered list of relevant products
        """
        # Start with all products
        filtered_products = all_products.copy()
        
        # Filter by category if specified
        if 'categories' in user_preferences and user_preferences['categories']:
            categories = user_preferences['categories']
            if isinstance(categories, str):
                categories = [categories]
            filtered_products = [p for p in filtered_products if p.get('category') in categories]
        
        # Filter by price range if specified
        if 'priceRange' in user_preferences:
            price_range = user_preferences['priceRange']
            if price_range == '0-50':
                filtered_products = [p for p in filtered_products if p.get('price', 0) <= 50]
            elif price_range == '50-100':
                filtered_products = [p for p in filtered_products if 50 <= p.get('price', 0) <= 100]
            elif price_range == '100+':
                filtered_products = [p for p in filtered_products if p.get('price', 0) >= 100]
        
        # Filter by brand if specified
        if 'brands' in user_preferences and user_preferences['brands']:
            brands = user_preferences['brands']
            if isinstance(brands, str):
                brands = [brands]
            filtered_products = [p for p in filtered_products if p.get('brand') in brands]
        
        # Calculate similarity to browsed products for remaining products
        if browsed_products:
            # Extract categories, subcategories, brands, and tags from browsed products
            browsed_categories = set(p.get('category') for p in browsed_products if p.get('category'))
            browsed_subcategories = set(p.get('subcategory') for p in browsed_products if p.get('subcategory'))
            browsed_brands = set(p.get('brand') for p in browsed_products if p.get('brand'))
            browsed_tags = set()
            for p in browsed_products:
                if p.get('tags'):
                    browsed_tags.update(p.get('tags'))
            
            # Score products based on similarity to browsed items
            scored_products = []
            for product in filtered_products:
                score = 0
                
                # Category match
                if product.get('category') in browsed_categories:
                    score += 3
                
                # Subcategory match
                if product.get('subcategory') in browsed_subcategories:
                    score += 2
                
                # Brand match
                if product.get('brand') in browsed_brands:
                    score += 2
                
                # Tag matches
                if product.get('tags'):
                    tag_matches = sum(1 for tag in product.get('tags') if tag in browsed_tags)
                    score += tag_matches
                
                # Add the product with its score
                scored_products.append((product, score))
            
            # Sort by score (highest first)
            scored_products.sort(key=lambda x: x[1], reverse=True)
            
            # Take top scoring products, plus some non-matching ones for diversity
            top_products = [p[0] for p in scored_products[:int(max_products * 0.7)]]
            
            # Add some products not browsed for diversity (up to max_products)
            diversity_products = [p[0] for p in scored_products[int(max_products * 0.7):]]
            
            # Ensure we're not exceeding max_products
            filtered_products = top_products + diversity_products[:max_products - len(top_products)]
        
        # If too few products remain after filtering, loosen criteria
        if len(filtered_products) < 10:
            filtered_products = all_products[:max_products]
        
        # Limit to max_products
        return filtered_products[:max_products]
    
    def _create_recommendation_prompt(self, user_preferences, browsed_products, relevant_products):
        """
        Create a prompt for the LLM to generate recommendations
        
        Parameters:
        - user_preferences (dict): User's stated preferences
        - browsed_products (list): Products the user has viewed
        - relevant_products (list): Pre-filtered relevant products
        
        Returns:
        - str: Prompt for the LLM
        """
        # Create a structured prompt with clear sections and instructions
        prompt = """
        You are an AI shopping assistant specializing in personalized product recommendations. 
        Your task is to suggest products that best match the user's explicit preferences and implicit interests shown in their browsing history.
        
        # USER PREFERENCES
        """
        
        # Add user preferences to the prompt with detailed formatting
        if user_preferences:
            price_range = user_preferences.get('priceRange', 'all')
            prompt += f"- Price Range: {price_range}\n"
            
            categories = user_preferences.get('categories', [])
            if categories:
                prompt += f"- Preferred Categories: {', '.join(categories)}\n"
                
            brands = user_preferences.get('brands', [])
            if brands:
                prompt += f"- Preferred Brands: {', '.join(brands)}\n"
        else:
            prompt += "- No explicit preferences provided\n"
        
        # Add browsing history section with detailed product information
        prompt += "\n# BROWSING HISTORY\n"
        
        if browsed_products:
            for product in browsed_products:
                prompt += f"- {product['name']} (ID: {product['id']})\n"
                prompt += f"  Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
                prompt += f"  Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}\n"
                if 'tags' in product and product['tags']:
                    prompt += f"  Tags: {', '.join(product['tags'])}\n"
                if 'features' in product and product['features']:
                    prompt += f"  Key Features: {', '.join(product['features'][:3])}\n"
                prompt += "\n"
        else:
            prompt += "- No browsing history available\n"
        
        # Extract behavioral patterns and preferences from browsing history
        if browsed_products:
            prompt += "\n# BEHAVIORAL INSIGHTS\n"
            
            # Extract and count categories
            categories = {}
            subcategories = {}
            brands = {}
            price_points = []
            tags = {}
            
            for product in browsed_products:
                # Count categories
                cat = product.get('category')
                if cat:
                    categories[cat] = categories.get(cat, 0) + 1
                
                # Count subcategories
                subcat = product.get('subcategory')
                if subcat:
                    subcategories[subcat] = subcategories.get(subcat, 0) + 1
                
                # Count brands
                brand = product.get('brand')
                if brand:
                    brands[brand] = brands.get(brand, 0) + 1
                
                # Track price points
                price = product.get('price')
                if price:
                    price_points.append(price)
                
                # Count tags
                if 'tags' in product and product['tags']:
                    for tag in product['tags']:
                        tags[tag] = tags.get(tag, 0) + 1
            
            # Add observed categories
            if categories:
                top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
                prompt += f"- Frequently browsed categories: {', '.join([f'{cat} ({count})' for cat, count in top_categories])}\n"
            
            # Add observed subcategories
            if subcategories:
                top_subcategories = sorted(subcategories.items(), key=lambda x: x[1], reverse=True)[:3]
                prompt += f"- Frequently browsed subcategories: {', '.join([f'{subcat} ({count})' for subcat, count in top_subcategories])}\n"
            
            # Add observed brands
            if brands:
                top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:3]
                prompt += f"- Preferred brands: {', '.join([f'{brand} ({count})' for brand, count in top_brands])}\n"
            
            # Add price range
            if price_points:
                avg_price = sum(price_points) / len(price_points)
                min_price = min(price_points)
                max_price = max(price_points)
                prompt += f"- Price behavior: Avg=${avg_price:.2f}, Range=${min_price:.2f}-${max_price:.2f}\n"
            
            # Add observed tags/interests
            if tags:
                top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:5]
                prompt += f"- Interest areas: {', '.join([f'{tag} ({count})' for tag, count in top_tags])}\n"
        
        # Add available products section (simplified to reduce tokens)
        prompt += "\n# AVAILABLE PRODUCTS\n"
        
        # Add simplified product information
        for product in relevant_products:
            prompt += f"ID: {product['id']} - {product['name']}\n"
            prompt += f"Category: {product.get('category', 'N/A')}, Subcategory: {product.get('subcategory', 'N/A')}\n"
            prompt += f"Brand: {product.get('brand', 'N/A')}, Price: ${product.get('price', 0)}, Rating: {product.get('rating', 'N/A')}\n"
            
            # Add description
            if 'description' in product:
                prompt += f"Description: {product['description']}\n"
            
            # Add tags
            if 'tags' in product and product['tags']:
                prompt += f"Tags: {', '.join(product['tags'])}\n"
            
            # Add key features (limited to 3 for brevity)
            if 'features' in product and product['features']:
                prompt += f"Features: {', '.join(product['features'][:3])}\n"
            
            prompt += "\n"
        
        # Add detailed instructions for the recommendations
        prompt += """
# RECOMMENDATION TASK
Based on the user's preferences and browsing history, recommend 5 products that would most interest them.

For each recommendation:
1. Consider how well it matches explicit preferences (categories, brands, price range)
2. Consider how it aligns with implicit interests shown in browsing history 
3. Include some products that expand on user interests (discovery)

# OUTPUT FORMAT
Return your recommendations as a valid JSON array in this exact structure:
[
  {
    "product_id": "product123",
    "relevance_score": 0.95,
    "explanation": "Detailed explanation of why this product is recommended"
  },
  ...
]

Ensure your recommendations have diverse relevance scores between 0.7-1.0 (don't make them all the same).
Each explanation should be personalized, mentioning specific user preferences or browsing patterns.
The JSON must be valid and parseable - this is critical.
"""
        
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
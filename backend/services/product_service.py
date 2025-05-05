"""
Product Service Implementation for AI-Powered Product Recommendation Engine

This service handles product data operations including loading, filtering,
and retrieving product information.
"""

import json
from config import config

class ProductService:
    """
    Service to handle product data operations
    """
    
    def __init__(self):
        """
        Initialize the product service with data path from config
        """
        self.data_path = config.get('DATA_PATH', 'data/products.json')
        self.products = self._load_products()
    
    def _load_products(self):
        """
        Load products from the JSON data file
        """
        try:
            with open(self.data_path, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading product data: {str(e)}")
            return []
    
    def get_all_products(self):
        """
        Return all products
        """
        return self.products
    
    def get_product_by_id(self, product_id):
        """
        Get a specific product by ID
        """
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def get_products(self, category=None, subcategory=None, min_price=None, 
                     max_price=None, brand=None, tags=None, min_rating=None,
                     search_query=None, limit=None, sort_by='name', sort_order='asc'):
        """
        Get products with filtering options
        
        Parameters:
        - category (str/list): Filter by category name(s)
        - subcategory (str/list): Filter by subcategory name(s)
        - min_price (float): Minimum price
        - max_price (float): Maximum price
        - brand (str/list): Filter by brand name(s)
        - tags (list): Filter by tags
        - min_rating (float): Minimum rating
        - search_query (str): Search query to match against name/description
        - limit (int): Maximum number of products to return
        - sort_by (str): Field to sort by
        - sort_order (str): 'asc' or 'desc'
        
        Returns:
        - list: Filtered products
        """
        filtered_products = self.products
        
        # Filter by category
        if category:
            if isinstance(category, list):
                filtered_products = [p for p in filtered_products if p.get('category') in category]
            else:
                filtered_products = [p for p in filtered_products if p.get('category') == category]
        
        # Filter by subcategory
        if subcategory:
            if isinstance(subcategory, list):
                filtered_products = [p for p in filtered_products if p.get('subcategory') in subcategory]
            else:
                filtered_products = [p for p in filtered_products if p.get('subcategory') == subcategory]
        
        # Filter by price range
        if min_price is not None:
            filtered_products = [p for p in filtered_products if p.get('price', 0) >= min_price]
        
        if max_price is not None:
            filtered_products = [p for p in filtered_products if p.get('price', 0) <= max_price]
        
        # Filter by brand
        if brand:
            if isinstance(brand, list):
                filtered_products = [p for p in filtered_products if p.get('brand') in brand]
            else:
                filtered_products = [p for p in filtered_products if p.get('brand') == brand]
        
        # Filter by tags
        if tags:
            filtered_products = [
                p for p in filtered_products 
                if p.get('tags') and any(tag in p.get('tags', []) for tag in tags)
            ]
        
        # Filter by rating
        if min_rating is not None:
            filtered_products = [p for p in filtered_products if p.get('rating', 0) >= min_rating]
        
        # Filter by search query
        if search_query:
            search_query = search_query.lower()
            filtered_products = [
                p for p in filtered_products 
                if (search_query in p.get('name', '').lower() or
                    search_query in p.get('description', '').lower() or
                    any(search_query in tag.lower() for tag in p.get('tags', [])))
            ]
        
        # Sort products
        if sort_by in ['name', 'price', 'rating']:
            reverse = sort_order.lower() == 'desc'
            filtered_products.sort(key=lambda p: p.get(sort_by, 0) if sort_by != 'name' else p.get(sort_by, '').lower(), 
                                 reverse=reverse)
        
        # Limit results
        if limit and limit > 0:
            filtered_products = filtered_products[:limit]
        
        return filtered_products
    
    def get_categories(self):
        """
        Get all unique product categories
        
        Returns:
        - list: Unique categories
        """
        categories = set()
        for product in self.products:
            if 'category' in product:
                categories.add(product['category'])
        return sorted(list(categories))
    
    def get_subcategories(self, category=None):
        """
        Get all unique product subcategories
        
        Parameters:
        - category (str): Optional category to filter subcategories
        
        Returns:
        - list: Unique subcategories
        """
        subcategories = set()
        for product in self.products:
            if 'subcategory' in product:
                if category is None or product.get('category') == category:
                    subcategories.add(product['subcategory'])
        return sorted(list(subcategories))
    
    def get_brands(self):
        """
        Get all unique product brands
        
        Returns:
        - list: Unique brands
        """
        brands = set()
        for product in self.products:
            if 'brand' in product:
                brands.add(product['brand'])
        return sorted(list(brands))
    
    def get_tags(self):
        """
        Get all unique product tags
        
        Returns:
        - list: Unique tags
        """
        tags = set()
        for product in self.products:
            if 'tags' in product:
                tags.update(product['tags'])
        return sorted(list(tags))
    
    def get_price_range(self):
        """
        Get the min and max product prices
        
        Returns:
        - dict: Min and max prices
        """
        prices = [p.get('price', 0) for p in self.products if 'price' in p]
        if not prices:
            return {'min': 0, 'max': 0}
        return {'min': min(prices), 'max': max(prices)}
    
    def get_related_products(self, product_id, limit=5):
        """
        Get products related to a specific product
        
        Parameters:
        - product_id (str): ID of the product to find related items for
        - limit (int): Maximum number of related products to return
        
        Returns:
        - list: Related products
        """
        # Get the source product
        source_product = self.get_product_by_id(product_id)
        if not source_product:
            return []
        
        # Calculate relatedness scores for all other products
        scored_products = []
        
        for product in self.products:
            # Skip the source product
            if product['id'] == product_id:
                continue
            
            score = 0
            
            # Same category
            if product.get('category') == source_product.get('category'):
                score += 3
            
            # Same subcategory
            if product.get('subcategory') == source_product.get('subcategory'):
                score += 2
            
            # Same brand
            if product.get('brand') == source_product.get('brand'):
                score += 1
            
            # Shared tags
            source_tags = set(source_product.get('tags', []))
            product_tags = set(product.get('tags', []))
            shared_tags = len(source_tags.intersection(product_tags))
            score += shared_tags
            
            # Similar price (within 20%)
            if 'price' in source_product and 'price' in product:
                price_ratio = product['price'] / source_product['price'] if source_product['price'] > 0 else 0
                if 0.8 <= price_ratio <= 1.2:
                    score += 1
            
            # Add to scored products if it has some relatedness
            if score > 0:
                scored_products.append((product, score))
        
        # Sort by score and return top results
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [p[0] for p in scored_products[:limit]]
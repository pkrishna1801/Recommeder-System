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
        self.data_path = config['DATA_PATH']
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
    
    def get_products_by_category(self, category):
        """
        Get products filtered by category
        """
        return [p for p in self.products if p['category'] == category]
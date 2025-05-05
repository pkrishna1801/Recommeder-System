# Modify your imports first
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import json
from services.llm_service import LLMService
from services.product_service import ProductService
from config import config
from services.embedding_service import EmbeddingService

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

product_service = ProductService()
embedding_service = EmbeddingService()  # Initialize embedding service
llm_service = LLMService()

# precompute embeddings for all products
@app.before_first_request
def precompute_embeddings():
    """Precompute embeddings for all products in the catalog"""
    try:
        logger.info("Precomputing embeddings for all products...")
        all_products = product_service.get_all_products()
        embedding_service.embed_all_products(all_products)
        logger.info(f"Embeddings computed for {len(all_products)} products")
    except Exception as e:
        logger.error(f"Error precomputing embeddings: {str(e)}")

@app.route('/api/products', methods=['GET'])
def get_products():
    """Endpoint to retrieve all products"""
    try:
        products = product_service.get_all_products()
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })
    except Exception as e:
        logger.error(f"Error in get_products: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """
    Endpoint to get details for a specific product
    """
    try:
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': f'Product with ID {product_id} not found'
            }), 404
            
        return jsonify({
            'success': True,
            'product': product
        })
    except Exception as e:
        logger.error(f"Error in get_product: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/categories', methods=['GET'])
def get_categories():
    """
    Endpoint to get all unique product categories
    """
    try:
        products = product_service.get_all_products()
        categories = sorted(list(set(p.get('category') for p in products if p.get('category'))))
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products/brands', methods=['GET'])
def get_brands():
    """
    Endpoint to get all unique product brands
    """
    try:
        products = product_service.get_all_products()
        brands = sorted(list(set(p.get('brand') for p in products if p.get('brand'))))
        
        return jsonify({
            'success': True,
            'brands': brands
        })
    except Exception as e:
        logger.error(f"Error in get_brands: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """
    Endpoint to generate personalized product recommendations
    based on user preferences and browsing history
    """
    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400
        
        # Extract user preferences and browsing history
        user_preferences = data.get('preferences', {})
        browsing_history = data.get('browsing_history', [])
        
        # Get all products
        all_products = product_service.get_all_products()
        
        # Generate recommendations
        recommendations = llm_service.generate_recommendations(
            user_preferences,
            browsing_history,
            all_products
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations.get('recommendations', []),
            'count': recommendations.get('count', 0)
        })
        
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
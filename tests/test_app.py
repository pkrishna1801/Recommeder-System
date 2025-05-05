import sys
import os
import pytest

# Add backend folder to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app import app as flask_app

# ------------------------
# Setup Flask test client
# ------------------------
@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

# ------------------------
# Helper: Get valid JWT token by logging in
# ------------------------
def get_token(client):
    response = client.post('/api/auth/login', json={
        "username": "ABC",
        "password": "Asdfgh"
    })
    assert response.status_code == 200
    return response.json.get("token")

# ------------------------
# 1. AUTH TEST CASES
# ------------------------

def test_register_user(client):
    response = client.post('/api/auth/register', json={
        "username": "ABC",
        "email": "ABC@gmail.com",
        "password": "Asdfgh"
    })
    assert response.status_code in [200, 201, 400]
    assert 'success' in response.json

def test_login_user(client):
    response = client.post('/api/auth/login', json={
        "username": "ABC",
        "password": "Asdfgh"
    })
    assert response.status_code in [200, 401]
    assert 'success' in response.json

# ------------------------
# 2. PRODUCT TEST CASES
# ------------------------

def test_get_all_products(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    assert 'products' in response.json

def test_get_product_by_invalid_id(client):
    response = client.get('/api/products/invalid_id')
    assert response.status_code in [404, 200]
    assert 'success' in response.json

def test_get_categories(client):
    response = client.get('/api/products/categories')
    assert response.status_code == 200
    assert 'categories' in response.json

def test_get_brands(client):
    response = client.get('/api/products/brands')
    assert response.status_code == 200
    assert 'brands' in response.json

def test_get_price_range(client):
    response = client.get('/api/products/price-range')
    assert response.status_code == 200
    assert 'price_range' in response.json

# ------------------------
# 3. RECOMMENDATION TEST CASES
# ------------------------

def test_get_recommendations_without_token(client):
    response = client.post('/api/recommendations', json={
        "preferences": {
            "category": ["electronics"],
            "brand": ["Apple"]
        },
        "browsing_history": ["product123", "product456"]
    })
    assert response.status_code == 200
    assert 'recommendations' in response.json

# ------------------------
# 4. AUTHENTICATED ROUTES (using dynamic token)
# ------------------------

def test_get_profile_with_valid_token(client):
    token = get_token(client)
    response = client.get('/api/user/profile', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert 'user' in response.json

def test_get_preferences_with_valid_token(client):
    token = get_token(client)
    response = client.get('/api/user/preferences', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert 'preferences' in response.json

def test_get_browsing_history_with_valid_token(client):
    token = get_token(client)
    response = client.get('/api/user/browsing-history', headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert 'browsing_history' in response.json

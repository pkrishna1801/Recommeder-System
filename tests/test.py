#!/usr/bin/env python
"""
Candidate Self-Evaluation Test Script

This script helps candidates test their implementation of the AI-Powered Product 
Recommendation Engine by running a series of basic tests on both the backend API
and the recommendation quality.

Usage:
    python candidate_test.py

Requirements:
    - Your FastAPI server must be running on http://localhost:5000
    - You must have requests and pytest libraries installed
"""

import json
import requests
import time
import sys

API_BASE_URL = "http://localhost:5000/api"

def print_header(message):
    print("\n" + "="*80)
    print(f" {message}")
    print("="*80)

def print_result(test_name, result, message=None):
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{status} - {test_name}")
    if message and not result:
        print(f"  → {message}")

def test_api_availability():
    """Test that the API is available and responding"""
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def test_products_endpoint():
    """Test that the products endpoint returns the expected data structure"""
    try:
        response = requests.get(f"{API_BASE_URL}/products")
        data = response.json()
        
        # Check that we have a list of products
        if not isinstance(data, list):
            return False, "Expected a list of products"
        
        # Check that we have at least 10 products
        if len(data) < 10:
            return False, "Expected at least 10 products"
        
        # Check that each product has the required fields
        required_fields = ["id", "name", "category", "price", "brand"]
        for product in data[:5]:  # Check the first 5 products
            for field in required_fields:
                if field not in product:
                    return False, f"Product missing required field: {field}"
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_recommendations_endpoint_structure():
    """Test that the recommendations endpoint accepts requests and returns the expected structure"""
    try:
        # Create a simple test request
        payload = {
            "preferences": {
                "priceRange": "all",
                "categories": ["Electronics"],
                "brands": []
            },
            "browsing_history": ["prod002", "prod007"]  # Electronics products
        }
        
        response = requests.post(f"{API_BASE_URL}/recommendations", json=payload)
        
        # Check response status
        if response.status_code != 200:
            return False, f"Expected status code 200, got {response.status_code}"
        
        data = response.json()
        
        # Check that we have recommendations
        if "recommendations" not in data:
            return False, "Response missing 'recommendations' field"
        
        # Check recommendations structure
        if not isinstance(data["recommendations"], list):
            return False, "Expected recommendations to be a list"
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_recommendation_quality_basic():
    """Test that recommendations are relevant to the provided preferences and browsing history"""
    try:
        # Test case: Electronics preference, browsing history of headphones and fitness watch
        payload = {
            "preferences": {
                "priceRange": "all",
                "categories": ["Electronics"],
                "brands": []
            },
            "browsing_history": ["prod002", "prod007"]  # Premium Wireless Headphones, Smart Fitness Watch
        }
        
        response = requests.post(f"{API_BASE_URL}/recommendations", json=payload)
        data = response.json()
        
        if not data.get("recommendations"):
            return False, "No recommendations returned"
        
        # Check that we have at least 3 recommendations
        if len(data["recommendations"]) < 3:
            return False, "Expected at least 3 recommendations"
        
        # For each recommendation, check if it contains a product and explanation
        for rec in data["recommendations"][:3]:  # Check the first 3
            if "product" not in rec:
                return False, "Recommendation missing 'product' field"
            if "explanation" not in rec:
                return False, "Recommendation missing 'explanation' field"
        
        # Count how many recommendations are from the Electronics category
        electronics_count = sum(1 for rec in data["recommendations"] 
                              if rec.get("product", {}).get("category") == "Electronics")
        
        # At least 50% of recommendations should be Electronics
        if electronics_count < len(data["recommendations"]) / 2:
            return False, "Too few recommendations from the preferred category"
        
        return True, None
    except Exception as e:
        return False, str(e)

def test_prompt_engineering_adaptation():
    """Test if recommendations adapt to different user preferences"""
    try:
        # Test case 1: Electronics preference
        payload1 = {
            "preferences": {
                "priceRange": "all",
                "categories": ["Electronics"],
                "brands": []
            },
            "browsing_history": []
        }
        
        # Test case 2: Home goods preference
        payload2 = {
            "preferences": {
                "priceRange": "all",
                "categories": ["Home"],
                "brands": []
            },
            "browsing_history": []
        }
        
        response1 = requests.post(f"{API_BASE_URL}/recommendations", json=payload1)
        data1 = response1.json()
        
        response2 = requests.post(f"{API_BASE_URL}/recommendations", json=payload2)
        data2 = response2.json()
        
        # Get product IDs from both recommendation sets
        rec_ids1 = [rec.get("product", {}).get("id") for rec in data1.get("recommendations", [])]
        rec_ids2 = [rec.get("product", {}).get("id") for rec in data2.get("recommendations", [])]
        
        # Check if the recommendations are different
        common_ids = set(rec_ids1).intersection(set(rec_ids2))
        
        # If more than 50% overlap, the recommendations might not be adapting well
        if len(common_ids) > min(len(rec_ids1), len(rec_ids2)) / 2:
            return False, "Recommendations don't adapt well to different preferences"
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    print_header("AI-Powered Product Recommendation Engine - Self-Evaluation Test")
    
    # Test API availability
    api_available = test_api_availability()
    print_result("API Availability", api_available, 
                "API not available. Make sure your FastAPI server is running on http://localhost:5000")
    
    if not api_available:
        print("\nCannot proceed with tests as the API is not available.")
        print("Please make sure your FastAPI server is running before executing this test script.")
        sys.exit(1)
    
    # Test products endpoint
    products_result, products_message = test_products_endpoint()
    print_result("Products Endpoint", products_result, products_message)
    
    # Test recommendations endpoint structure
    rec_structure_result, rec_structure_message = test_recommendations_endpoint_structure()
    print_result("Recommendations Endpoint Structure", rec_structure_result, rec_structure_message)
    
    # Test recommendation quality
    rec_quality_result, rec_quality_message = test_recommendation_quality_basic()
    print_result("Basic Recommendation Quality", rec_quality_result, rec_quality_message)
    
    # Test prompt engineering adaptation
    prompt_adapt_result, prompt_adapt_message = test_prompt_engineering_adaptation()
    print_result("Prompt Engineering Adaptation", prompt_adapt_result, prompt_adapt_message)
    
    # Summary
    print("\n" + "-"*80)
    tests_passed = sum([
        api_available, 
        products_result, 
        rec_structure_result, 
        rec_quality_result,
        prompt_adapt_result
    ])
    total_tests = 5
    
    print(f"Tests passed: {tests_passed}/{total_tests} ({tests_passed/total_tests*100:.0f}%)")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Your implementation meets the basic requirements.")
    else:
        print("\n⚠️  Some tests failed. Review the output above to see what needs improvement.")
    
    print("\nNote: This is just a basic test script. The actual evaluation will be more thorough.")
    print("Make sure to thoroughly test your prompt engineering and user experience beyond these tests.")

if __name__ == "__main__":
    main()
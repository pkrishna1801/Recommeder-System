"""
Benchmark script to compare FAISS vs scikit-learn performance
"""
import json
import time
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import faiss

# Load products
def load_products(max_products=None):
    with open('data/products.json', 'r') as f:
        products = json.load(f)
        if max_products:
            return products[:max_products]
        return products

# Create random embeddings for testing (to avoid API calls)
def create_random_embeddings(num_products, dim=1536):
    embeddings = np.random.randn(num_products, dim).astype(np.float32)
    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings

# Benchmark FAISS search
def benchmark_faiss(embeddings, query_embedding, top_k=10, num_runs=10):
    # Setup FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    # Benchmark search
    start_time = time.time()
    for _ in range(num_runs):
        distances, indices = index.search(query_embedding.reshape(1, -1), top_k)
    end_time = time.time()
    
    # Ensure we don't get zero by using max with a small value
    avg_time = max((end_time - start_time) / num_runs, 0.000001)
    return {
        "method": "FAISS",
        "avg_time_ms": avg_time * 1000,
        "results": indices[0].tolist()
    }

# Benchmark scikit-learn search
def benchmark_sklearn(embeddings, query_embedding, top_k=10, num_runs=10):
    start_time = time.time()
    for _ in range(num_runs):
        similarities = cosine_similarity(query_embedding.reshape(1, -1), embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
    end_time = time.time()
    
    # Ensure we don't get zero by using max with a small value
    avg_time = max((end_time - start_time) / num_runs, 0.000001)
    return {
        "method": "scikit-learn",
        "avg_time_ms": avg_time * 1000,
        "results": top_indices.tolist()
    }

# Run benchmarks with different catalog sizes
def run_benchmarks():
    # Using smaller sizes for initial testing and adding more realistic sizes
    catalog_sizes = [50, 100, 500, 1000]
    results = []
    
    print("Benchmarking FAISS vs scikit-learn...")
    print(f"{'Size':<10} {'FAISS (ms)':<15} {'scikit-learn (ms)':<20} {'Speedup':<10}")
    print("-" * 55)
    
    for size in catalog_sizes:
        # Create random embeddings
        embeddings = create_random_embeddings(size)
        # Create a random query embedding
        query_embedding = create_random_embeddings(1)[0]
        
        # Run benchmarks
        faiss_result = benchmark_faiss(embeddings, query_embedding)
        sklearn_result = benchmark_sklearn(embeddings, query_embedding)
        
        # Calculate speedup - ensure we don't divide by zero
        speedup = sklearn_result["avg_time_ms"] / max(faiss_result["avg_time_ms"], 0.001)
        
        print(f"{size:<10} {faiss_result['avg_time_ms']:<15.3f} {sklearn_result['avg_time_ms']:<20.3f} {speedup:<10.2f}x")
        
        results.append({
            "catalog_size": size,
            "faiss_time_ms": faiss_result["avg_time_ms"],
            "sklearn_time_ms": sklearn_result["avg_time_ms"],
            "speedup": speedup
        })
    
    return results

# Token usage simulation with real product data
def estimate_token_reduction():
    # Load actual products
    try:
        products = load_products()
    except Exception as e:
        print(f"Error loading products: {str(e)}")
        # Create dummy products if file not found
        products = [
            {"id": f"prod{i}", "name": f"Product {i}", "category": "Category", 
             "brand": "Brand", "price": 99.99, "description": "Product description",
             "features": ["Feature 1", "Feature 2"]} for i in range(50)
        ]
    
    # Select a few products to simulate browsing history
    browsed_indices = [0, 2]  # First and third products
    browsed_products = [products[i] for i in browsed_indices]
    
    print("\nToken Usage Estimation:")
    print("-----------------------")
    
    # Original approach: Send 30 products
    original_product_count = min(30, len(products))
    original_products = products[:original_product_count]
    
    # Create a simple text representation
    original_text = "User browsing history:\n"
    for p in browsed_products:
        original_text += f"- {p['name']} ({p.get('category', 'N/A')})\n"
    
    original_text += "\nAvailable products:\n"
    for p in original_products:
        original_text += f"- {p['name']} ({p.get('category', 'N/A')}, {p.get('brand', 'N/A')}, ${p.get('price', 0)})\n"
        description = p.get('description', '')
        if description:
            original_text += f"  Description: {description[:100]}\n"
        features = p.get('features', [])
        if features:
            original_text += f"  Features: {', '.join(features[:3])}\n\n"
    
    # RAG approach: Send 10 most relevant products
    rag_product_count = min(10, len(products))
    rag_products = products[:rag_product_count]  # Simulating the most relevant ones
    
    rag_text = "User browsing history:\n"
    for p in browsed_products:
        rag_text += f"- {p['name']} ({p.get('category', 'N/A')})\n"
    
    rag_text += "\nRecommendation candidates:\n"
    for p in rag_products:
        rag_text += f"- {p['name']} ({p.get('category', 'N/A')}, ${p.get('price', 0)})\n"
    
    # Estimate tokens (rough approximation: ~4 chars per token)
    original_tokens = len(original_text) // 4
    rag_tokens = len(rag_text) // 4
    token_reduction = (original_tokens - rag_tokens) / original_tokens * 100
    
    print(f"Original approach ({original_product_count} products): ~{original_tokens} tokens")
    print(f"RAG approach ({rag_product_count} products): ~{rag_tokens} tokens")
    print(f"Token reduction: {token_reduction:.1f}%")
    
    return {
        "original_tokens": original_tokens,
        "rag_tokens": rag_tokens,
        "reduction_percentage": token_reduction
    }

if __name__ == "__main__":
    print("FAISS vs scikit-learn Benchmark")
    print("==============================")
    
    # Run performance benchmarks
    run_benchmarks()
    
    # Estimate token reduction
    estimate_token_reduction()
    
    print("\nNote: For even better performance with large catalogs (100K+ products),")
    print("consider using approximate nearest neighbor indices like FAISS IVF or HNSW.")
import requests
import time

def test_query_performance():
    """Test query endpoint performance"""
    url = "http://localhost:8000/api/query"
    
    queries = [
        "TSMC",
        "NVIDIA AI chips",
        "Intel foundry",
        "TSMC",  # Repeat to test cache
    ]
    
    print("=" * 60)
    print("QUERY PERFORMANCE TEST")
    print("=" * 60)
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        start = time.time()
        response = requests.post(url, json={"query": query, "k": 5})
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            evidence_count = len(data.get("evidence", []))
            signal_strength = data.get("signal_strength", 0)
            
            print(f"   ✅ Response time: {elapsed:.1f}ms")
            print(f"   📊 Evidence: {evidence_count} items")
            print(f"   📈 Signal strength: {signal_strength}%")
            
            if elapsed < 1000:
                print(f"   🚀 FAST - Target achieved!")
            elif elapsed < 2000:
                print(f"   ⚡ Good - Under 2s")
            else:
                print(f"   ⚠️  Slow - Needs optimization")
        else:
            print(f"   ❌ Error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_query_performance()

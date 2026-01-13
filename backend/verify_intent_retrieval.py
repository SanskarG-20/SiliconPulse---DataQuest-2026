import urllib.request
import json
import time

BASE_URL = "http://localhost:8000"

def post_json(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def test_intent_retrieval():
    print("=== Testing Intent-Aware Retrieval ===")
    
    # 1. Inject Test Data
    print("\n1. Injecting Test Data...")
    events = [
        {
            "title": "NVIDIA Launches New Blackwell GPU",
            "content": "NVIDIA announced the release of its latest Blackwell B200 GPU for AI workloads.",
            "source": "TechCrunch",
            "timestamp": "2024-03-18T10:00:00Z"
        },
        {
            "title": "NVIDIA Signs Contract with TSMC",
            "content": "NVIDIA has signed a new long-term supply agreement with TSMC for 3nm wafers.",
            "source": "Reuters",
            "timestamp": "2024-03-17T10:00:00Z"
        },
        {
            "title": "NVIDIA Earnings Report Q1",
            "content": "NVIDIA reported record revenue for Q1 driven by data center demand.",
            "source": "Bloomberg",
            "timestamp": "2024-03-16T10:00:00Z"
        }
    ]
    
    for event in events:
        try:
            post_json(f"{BASE_URL}/api/inject", event)
        except Exception as e:
            print(f"Injection failed: {e}")
            
    time.sleep(2) # Wait for cache refresh
    
    # 2. Test Product Launch Intent
    print("\n2. Testing 'Product Launch' Intent...")
    query = "latest product of nvidia"
    try:
        response = post_json(f"{BASE_URL}/api/query", {"query": query, "k": 5})
        evidence = response.get("evidence", [])
        print(f"Query: {query}")
        print(f"Top Result: {evidence[0]['title'] if evidence else 'None'}")
        
        if evidence and "Launch" in evidence[0]["title"]:
            print("PASS: Product launch event ranked first.")
        else:
            print("FAIL: Product launch event NOT ranked first.")
            
        # Check event type
        if evidence and evidence[0].get("event_type") == "product_launch":
             print("PASS: Event type correctly classified as 'product_launch'.")
        else:
             print(f"FAIL: Event type is {evidence[0].get('event_type') if evidence else 'None'}")
             
    except Exception as e:
        print(f"Query failed: {e}")
        
    # 3. Test Contract Intent
    print("\n3. Testing 'Contract' Intent...")
    query = "nvidia tsmc contract"
    try:
        response = post_json(f"{BASE_URL}/api/query", {"query": query, "k": 5})
        evidence = response.get("evidence", [])
        print(f"Query: {query}")
        print(f"Top Result: {evidence[0]['title'] if evidence else 'None'}")
        
        if evidence and "Contract" in evidence[0]["title"]:
            print("PASS: Contract event ranked first.")
        else:
            print("FAIL: Contract event NOT ranked first.")
            
        # Check event type
        if evidence and evidence[0].get("event_type") == "contract":
             print("PASS: Event type correctly classified as 'contract'.")
        else:
             print(f"FAIL: Event type is {evidence[0].get('event_type') if evidence else 'None'}")
             
    except Exception as e:
        print(f"Query failed: {e}")

if __name__ == "__main__":
    try:
        test_intent_retrieval()
    except Exception as e:
        print(f"Test Failed: {e}")

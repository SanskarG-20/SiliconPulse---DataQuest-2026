
import urllib.request
import json
import time

def verify_tech_giants_search():
    # 1. Bootstrap new data (to ensure coverage)
    print("Bootstrapping new data...")
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/bootstrap", method="POST")
        with urllib.request.urlopen(req) as response:
            print(f"Bootstrap Status: {response.status}")
    except Exception as e:
        print(f"Bootstrap Failed: {e}")
        return

    time.sleep(2) # Wait for cache refresh

    # 2. Test Queries
    queries = [
        "latest updates about Microsoft",
        "Amazon AI chip updates",
        "Meta acquisitions",
        "NVIDIA Blackwell news",
        "Apple supply chain"
    ]
    
    for q in queries:
        print(f"\nSearching for '{q}'...")
        payload = {
            "query": q,
            "k": 5
        }
        
        try:
            req = urllib.request.Request(
                "http://127.0.0.1:8000/api/query", 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'},
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                evidence = data.get("evidence", [])
                print(f"Found {len(evidence)} evidence items.")
                
                if len(evidence) > 0:
                    print(f"SUCCESS: Found evidence for '{q}'")
                    for item in evidence:
                         print(f"- [{item.get('company')}] {item.get('title')}")
                else:
                    print(f"FAILURE: No evidence found for '{q}'")
                    
        except Exception as e:
            print(f"Query Failed: {e}")

if __name__ == "__main__":
    verify_tech_giants_search()

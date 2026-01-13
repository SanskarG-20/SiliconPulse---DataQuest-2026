import urllib.request
import json

BASE_URL = "http://localhost:8000"

def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def verify_snippets():
    print("=== Verifying Snippets ===")
    
    # 1. Test /api/signals (used for live ticker)
    print("\n1. Testing /api/signals...")
    try:
        events = get_json(f"{BASE_URL}/api/signals")
        print(f"Received {len(events)} events.")
        
        valid_snippets = 0
        for event in events:
            snippet = event.get("snippet", "")
            # Note: /api/signals might not return snippet if it's just raw event
            # But let's check if it has it
            if snippet and len(snippet) > 20:
                valid_snippets += 1
                if valid_snippets <= 3:
                    print(f"  - Snippet: {snippet[:50]}...")
        
        print(f"Found {valid_snippets} events with valid snippets in /api/signals.")
            
    except Exception as e:
        print(f"FAIL: /api/signals failed: {e}")

    # 2. Test /api/query (used for main list)
    print("\n2. Testing /api/query...")
    try:
        req_data = json.dumps({"query": "latest news", "k": 10}).encode('utf-8')
        req = urllib.request.Request(f"{BASE_URL}/api/query", data=req_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        evidence = result.get("evidence", [])
        print(f"Received {len(evidence)} evidence items.")
        
        valid_snippets = 0
        for item in evidence:
            snippet = item.get("snippet", "")
            if snippet and len(snippet) > 20 and snippet != "...":
                valid_snippets += 1
                if valid_snippets <= 3:
                    print(f"  - Snippet: {snippet[:50]}...")
            else:
                print(f"  - Invalid Snippet: '{snippet}'")
        
        if valid_snippets > 0:
            print(f"PASS: Found {valid_snippets} items with valid snippets in /api/query.")
        else:
            print("FAIL: No valid snippets found in /api/query.")

    except Exception as e:
        print(f"FAIL: /api/query failed: {e}")

if __name__ == "__main__":
    verify_snippets()

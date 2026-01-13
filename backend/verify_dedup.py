import urllib.request
import json

BASE_URL = "http://localhost:8000"

def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def verify_deduplication():
    print("=== Verifying Deduplication ===")
    
    # 1. Test /api/signals
    print("\n1. Testing /api/signals...")
    try:
        events = get_json(f"{BASE_URL}/api/signals")
        print(f"Received {len(events)} events.")
        
        seen = set()
        duplicates = []
        for event in events:
            key = (event.get("title"), event.get("source"))
            if key in seen:
                duplicates.append(key)
            seen.add(key)
            
        if duplicates:
            print(f"FAIL: Found {len(duplicates)} duplicates in /api/signals.")
            for d in duplicates:
                print(f"  - {d}")
        else:
            print("PASS: No duplicates found in /api/signals.")
            
    except Exception as e:
        print(f"FAIL: /api/signals failed: {e}")

if __name__ == "__main__":
    verify_deduplication()

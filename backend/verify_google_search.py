
import urllib.request
import json
import time

def verify_google_search():
    # 1. Bootstrap new data (to ensure Google events exist)
    print("Bootstrapping new data...")
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/bootstrap", method="POST")
        with urllib.request.urlopen(req) as response:
            print(f"Bootstrap Status: {response.status}")
    except Exception as e:
        print(f"Bootstrap Failed: {e}")
        return

    time.sleep(2) # Wait for cache refresh

    # 2. Search for "google updates"
    print("\nSearching for 'google updates'...")
    payload = {
        "query": "google updates",
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
            
            found_google = False
            for item in evidence:
                print(f"- [{item.get('company')}] {item.get('title')}")
                if item.get('company') in ["Google", "Alphabet", "DeepMind"]:
                    found_google = True
                    
            if found_google:
                print("\nSUCCESS: Found Google-related evidence!")
            else:
                print("\nFAILURE: No Google-related evidence found.")
                
    except Exception as e:
        print(f"Query Failed: {e}")

if __name__ == "__main__":
    verify_google_search()

import urllib.request
import json
import time

BASE_URL = "http://localhost:8000"

def get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def verify_fix():
    print("=== Verifying Fix for Recommendation Error ===")
    
    # 1. Test Recommendations
    print("\n1. Testing /api/recommendations...")
    try:
        data = get_json(f"{BASE_URL}/api/recommendations")
        print("SUCCESS: /api/recommendations returned 200 OK")
        print(f"Generated at: {data.get('generated_at')}")
    except Exception as e:
        print(f"FAIL: /api/recommendations failed: {e}")

    # 2. Test Radar (if it exists)
    print("\n2. Testing /api/radar...")
    try:
        # Note: I haven't seen the exact path for radar, assuming /api/radar based on logs
        data = get_json(f"{BASE_URL}/api/radar")
        print("SUCCESS: /api/radar returned 200 OK")
    except Exception as e:
        print(f"FAIL: /api/radar failed: {e}")
        # Try /api/signals just in case
        try:
             data = get_json(f"{BASE_URL}/api/signals")
             print("SUCCESS: /api/signals returned 200 OK")
        except Exception as ex:
             print(f"FAIL: /api/signals failed: {ex}")

if __name__ == "__main__":
    verify_fix()

import requests
import json

print("=" * 70)
print("TESTING ALL SILICONPULSE API ENDPOINTS")
print("=" * 70)

base_url = "http://localhost:8000"

# Test 1: Health endpoint
print("\n[1] Testing GET /health...")
try:
    response = requests.get(f"{base_url}/health")
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Root endpoint
print("\n[2] Testing GET /...")
try:
    response = requests.get(f"{base_url}/")
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 3: Inject endpoint
print("\n[3] Testing POST /api/inject...")
try:
    data = {
        "title": "AI Breakthrough",
        "content": "Major advancement in artificial intelligence announced"
    }
    response = requests.post(f"{base_url}/api/inject", json=data)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Query endpoint
print("\n[4] Testing POST /api/query...")
try:
    data = {
        "query": "artificial intelligence",
        "k": 5
    }
    response = requests.post(f"{base_url}/api/query", json=data)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"    Query: {result.get('query')}")
        print(f"    Evidence count: {len(result.get('evidence', []))}")
        print(f"    Signal strength: {result.get('signal_strength')}")
    else:
        print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 5: Signals endpoint
print("\n[5] Testing GET /api/signals...")
try:
    response = requests.get(f"{base_url}/api/signals")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        signals = response.json()
        print(f"    Signals count: {len(signals)}")
    else:
        print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 6: Radar endpoint
print("\n[6] Testing GET /api/radar...")
try:
    response = requests.get(f"{base_url}/api/radar")
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        radar = response.json()
        print(f"    Companies tracked: {len(radar)}")
    else:
        print(f"    Response: {response.json()}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)

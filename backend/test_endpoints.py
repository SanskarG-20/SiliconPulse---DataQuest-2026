import requests
import json

# Test 1: Inject endpoint
print("Testing POST /api/inject...")
inject_data = {
    "title": "Test Event",
    "content": "This is a test event for SiliconPulse backend testing"
}

try:
    response = requests.post("http://localhost:8000/api/inject", json=inject_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 2: Inject another event
print("Testing POST /api/inject (second event)...")
inject_data2 = {
    "title": "AI Breakthrough",
    "content": "Major advancement in artificial intelligence technology announced today"
}

try:
    response = requests.post("http://localhost:8000/api/inject", json=inject_data2)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
except Exception as e:
    print(f"Error: {e}")
    print()

# Test 3: Query endpoint
print("Testing POST /api/query...")
query_data = {
    "query": "test event",
    "k": 5
}

try:
    response = requests.post("http://localhost:8000/api/query", json=query_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

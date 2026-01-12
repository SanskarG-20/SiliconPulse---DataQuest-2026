import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_query_hardening():
    print("🚀 Testing /api/query hardening...")
    
    # Test 1: Normal Query
    print("\n1. Normal Query:")
    try:
        response = requests.post(f"{BASE_URL}/query", json={"query": "nvidia", "k": 5})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Empty Query (Should return empty evidence, 200 OK)
    print("\n2. Empty Query:")
    try:
        response = requests.post(f"{BASE_URL}/query", json={"query": "", "k": 5})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data['evidence'] == []:
                print("✅ Success (Empty evidence returned)")
            else:
                print("⚠️ Unexpected evidence")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Malformed Body (Should be handled by FastAPI validation, returning 422, which is fine, but we want to ensure no 500)
    print("\n3. Malformed Body:")
    try:
        response = requests.post(f"{BASE_URL}/query", data="invalid json")
        print(f"Status: {response.status_code}")
        if response.status_code != 500:
            print("✅ Success (Not 500)")
        else:
            print("❌ Failed (Returned 500)")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_query_hardening()

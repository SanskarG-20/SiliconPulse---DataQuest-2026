import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_gemini_config():
    print("🚀 Testing Gemini Configuration...")
    
    # 1. Check Health
    print("\n1. Checking Health (/api/llm/health)...")
    try:
        response = requests.get(f"{BASE_URL}/llm/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            if data.get("generation_test") == "success":
                print("✅ Health Check Passed")
            else:
                print("⚠️ Health Check Warning: Generation failed (check API key)")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # 2. List Models
    print("\n2. Listing Models (/api/llm/models)...")
    try:
        response = requests.get(f"{BASE_URL}/llm/models")
        if response.status_code == 200:
            models = response.json()
            print(f"Found {len(models)} models")
            for m in models[:3]: # Show first 3
                print(f"- {m['name']}")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gemini_config()

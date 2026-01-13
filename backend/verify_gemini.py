
import urllib.request
import json
import time

def test_llm_health():
    url = "http://127.0.0.1:8000/api/llm/health"
    print(f"Testing LLM Health Endpoint: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            print(f"Status Code: {status_code}")
            
            if status_code == 200:
                data = json.loads(response.read().decode('utf-8'))
                print("Response JSON:")
                print(json.dumps(data, indent=2))
                
                if data.get("available_models"):
                    print(f"\nSUCCESS: Available models: {data['available_models']}")
                    if data.get("generation_test") == "success":
                         print(f"Generation test passed with model: {data.get('tested_model')}")
                    return True
                else:
                    print("\nWARNING: No models found.")
                    return True
            else:
                print(f"\nFAILURE: Unexpected status code {status_code}")
                return False
            
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        return False

if __name__ == "__main__":
    if test_llm_health():
        print("TEST PASSED")
    else:
        print("TEST FAILED")

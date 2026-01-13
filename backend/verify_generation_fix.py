
import urllib.request
import json
import time

def test_generation():
    url = "http://127.0.0.1:8000/api/generate"
    print(f"Testing Generation Endpoint: {url}")
    
    # Test Case 1: Low Evidence (Should Fallback)
    print("\nTest Case 1: Low Evidence (< 2 items)")
    payload_low = {
        "query": "Test Query",
        "context": "Only one evidence item here."
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload_low).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print("Response Insight:")
            print(data.get("insight")[:100] + "...")
            
            if "Insufficient Data" in data.get("insight", ""):
                print("SUCCESS: Correctly gated low evidence.")
            else:
                print("FAILURE: Did not gate low evidence.")
                
    except Exception as e:
        print(f"EXCEPTION (Case 1): {e}")

    # Test Case 2: Sufficient Evidence (Should Call Gemini - or fail if no key, but pass gate)
    print("\nTest Case 2: Sufficient Evidence (>= 2 items)")
    # Simulating context with timestamps to pass the count check
    context_high = """
    [2024-01-01 | Source A] Evidence 1
    [2024-01-02 | Source B] Evidence 2
    [2024-01-03 | Source C] Evidence 3
    """
    payload_high = {
        "query": "Test Query",
        "context": context_high
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload_high).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            insight = data.get("insight", "")
            print("Response Insight:")
            print(insight[:100] + "...")
            
            if "Insufficient Data" not in insight:
                print("SUCCESS: Passed gate with sufficient evidence.")
            else:
                print("FAILURE: Incorrectly gated sufficient evidence.")
                
    except Exception as e:
        print(f"EXCEPTION (Case 2): {e}")

if __name__ == "__main__":
    test_generation()

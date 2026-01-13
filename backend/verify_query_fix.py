
import urllib.request
import json
import time
import sys

def test_query():
    url = "http://127.0.0.1:8000/api/query"
    payload = {
        "query": "TSMC",
        "k": 5
    }
    
    print(f"Testing Query Endpoint: {url}")
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            print(f"Status Code: {status_code}")
            
            if status_code == 200:
                response_body = response.read().decode('utf-8')
                data = json.loads(response_body)
                print("Response JSON:")
                print(json.dumps(data, indent=2))
                
                if "evidence" in data and "signal_strength" in data:
                    print("\nSUCCESS: Query endpoint returned valid structure.")
                    return True
                else:
                    print("\nFAILURE: Response missing required fields.")
                    return False
            else:
                print(f"\nFAILURE: Unexpected status code {status_code}")
                return False
            
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        return False

if __name__ == "__main__":
    if test_query():
        print("TEST PASSED")
    else:
        print("TEST FAILED")

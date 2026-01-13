
import urllib.request
import json

def test_recommendations():
    url = "http://127.0.0.1:8000/api/recommendations"
    print(f"Testing Recommendations Endpoint: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            status_code = response.getcode()
            print(f"Status Code: {status_code}")
            
            if status_code == 200:
                data = json.loads(response.read().decode('utf-8'))
                print("Response JSON:")
                print(json.dumps(data, indent=2))
                
                if data.get("recommended_queries") and len(data["recommended_queries"]) == 4:
                    print(f"\nSUCCESS: Received {len(data['recommended_queries'])} recommendations.")
                    return True
                else:
                    print("\nFAILURE: Invalid recommendations format or count.")
                    return False
            else:
                print(f"\nFAILURE: Unexpected status code {status_code}")
                return False
            
    except Exception as e:
        print(f"\nEXCEPTION: {e}")
        return False

if __name__ == "__main__":
    if test_recommendations():
        print("TEST PASSED")
    else:
        print("TEST FAILED")

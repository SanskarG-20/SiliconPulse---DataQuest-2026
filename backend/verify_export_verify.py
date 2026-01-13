
import urllib.request
import json
import time

def verify_export_verify():
    # 1. Test Verify Sources Endpoint
    print("Testing Verify Sources...")
    try:
        query = "latest updates about Microsoft"
        url = f"http://127.0.0.1:8000/api/sources/verify?query={urllib.parse.quote(query)}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"Verify Status: {response.status}")
            print(f"Sources Found: {len(data.get('sources', []))}")
            if len(data.get('sources', [])) > 0:
                print(f"Sample Source: {data['sources'][0]}")
            else:
                print("WARNING: No sources found to verify.")
    except Exception as e:
        print(f"Verify Failed: {e}")

    # 2. Test Export Endpoint
    print("\nTesting Export Analysis...")
    try:
        payload = {
            "query": "Test Query",
            "report": "This is a test report.",
            "evidence": [
                {
                    "title": "Test Evidence",
                    "snippet": "Test Snippet",
                    "source": "Test Source",
                    "timestamp": "2023-01-01T00:00:00",
                    "url": "http://example.com"
                }
            ],
            "format": "md"
        }
        
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/export", 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'},
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            print(f"Export Status: {response.status}")
            content_disp = response.headers.get('Content-Disposition')
            print(f"Content-Disposition: {content_disp}")
            content = response.read().decode('utf-8')
            print(f"Content Length: {len(content)}")
            if "# SiliconPulse Intelligence Report" in content:
                print("SUCCESS: Export content valid.")
            else:
                print("FAILURE: Export content invalid.")
                
    except Exception as e:
        print(f"Export Failed: {e}")

if __name__ == "__main__":
    verify_export_verify()

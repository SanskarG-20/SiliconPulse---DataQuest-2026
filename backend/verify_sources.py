import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_pull_all():
    print("Testing /api/sources/pull_all...")
    try:
        response = requests.post(f"{BASE_URL}/sources/pull_all")
        if response.status_code == 200:
            print("✅ Success:", json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_stream_content():
    print("\nVerifying stream.jsonl content...")
    try:
        with open("data/stream.jsonl", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        perplexity_count = 0
        x_count = 0
        
        for line in lines[-20:]:  # Check last 20 lines
            event = json.loads(line)
            source = event.get("source")
            if source == "Perplexity":
                perplexity_count += 1
            elif source == "X":
                x_count += 1
                
        print(f"Found {perplexity_count} Perplexity events and {x_count} X events in last 20 entries.")
        
        if perplexity_count > 0 and x_count > 0:
            print("✅ Data ingestion verified!")
        else:
            print("⚠️ Warning: New data might not be present yet.")
            
    except Exception as e:
        print(f"❌ Error reading stream: {e}")

if __name__ == "__main__":
    test_pull_all()
    time.sleep(1)
    verify_stream_content()

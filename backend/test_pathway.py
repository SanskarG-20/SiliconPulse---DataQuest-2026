import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def test_pathway_flow():
    print("🧪 Starting Pathway Integration Test...")
    
    # 1. Check initial signals
    print("📡 Checking initial signals...")
    try:
        resp = requests.get(f"{BASE_URL}/signals")
        initial_count = len(resp.json())
        print(f"✅ Received {initial_count} initial signals")
    except Exception as e:
        print(f"❌ Failed to connect to backend: {e}")
        return

    # 2. Inject a unique signal
    test_id = int(time.time())
    test_title = f"PATHWAY_TEST_SIGNAL_{test_id}"
    test_content = f"This is a test signal for Pathway pipeline verification. Keywords: NVIDIA, TSMC, contract."
    
    print(f"💉 Injecting test signal: {test_title}")
    payload = {
        "title": test_title,
        "content": test_content,
        "source": "PathwayTester"
    }
    
    resp = requests.post(f"{BASE_URL}/inject", json=payload)
    if resp.status_code == 200:
        print("✅ Signal injected successfully")
    else:
        print(f"❌ Injection failed: {resp.text}")
        return

    # 3. Wait for Pathway to process
    print("⏳ Waiting 5 seconds for Pathway processing...")
    time.sleep(5)

    # 4. Confirm signal appears in feed
    print("📡 Verifying signal in feed...")
    resp = requests.get(f"{BASE_URL}/signals")
    signals = resp.json()
    
    found = False
    for s in signals:
        if s.get("title") == test_title:
            found = True
            print(f"✅ SUCCESS: Found processed signal in feed!")
            print(f"   - Company: {s.get('company')}")
            print(f"   - Event Type: {s.get('event_type')}")
            break
            
    if not found:
        print("❌ FAILED: Injected signal not found in feed after processing window.")
        print("   Check if pathway_pipeline.py is running and writing to data/pathway_out.jsonl")

if __name__ == "__main__":
    test_pathway_flow()

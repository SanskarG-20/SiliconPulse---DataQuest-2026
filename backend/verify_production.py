import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def log(msg):
    print(msg)
    with open("verification_result.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def check(name, success):
    if success:
        log(f"✅ {name}: PASS")
    else:
        log(f"❌ {name}: FAIL")
        # Don't exit immediately, run all checks
        # sys.exit(1) 

def verify_production():
    with open("verification_result.txt", "w", encoding="utf-8") as f:
        f.write("PRODUCTION VERIFICATION SUITE\n=============================\n")

    log("Starting verification...")
    
    # Warmup
    try:
        requests.get(f"{BASE_URL}/health")
        time.sleep(1)
    except:
        pass

    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health")
        check("Health Check", r.status_code == 200 and r.json()["status"] == "online")
    except Exception as e:
        log(f"Health check failed: {e}")

    # 2. Query Endpoint (Happy Path)
    try:
        start = time.time()
        r = requests.post(f"{API_URL}/query", json={"query": "TSMC", "k": 5})
        elapsed = time.time() - start
        data = r.json()
        
        check("Query Status 200", r.status_code == 200)
        check("Query Response Schema", "evidence" in data and "signal_strength" in data)
        # Relaxed latency check for test environment
        check("Query Latency < 2s", elapsed < 2.0)
        log(f"   Latency: {elapsed*1000:.1f}ms")
    except Exception as e:
        log(f"Query Endpoint Error: {e}")
        if 'r' in locals():
            log(f"   Status: {r.status_code}")
            log(f"   Response: {r.text[:200]}")
        check("Query Endpoint", False)

    # 3. Query Endpoint (Empty Query)
    try:
        r = requests.post(f"{API_URL}/query", json={"query": "", "k": 5})
        check("Empty Query Handled", r.status_code == 200 and len(r.json()["evidence"]) == 0)
    except:
        check("Empty Query", False)

    # 4. Signals Endpoint
    try:
        r = requests.get(f"{API_URL}/signals")
        check("Signals Endpoint", r.status_code == 200 and isinstance(r.json(), list))
    except:
        check("Signals Endpoint", False)

    # 5. Radar Endpoint
    try:
        r = requests.get(f"{API_URL}/radar")
        check("Radar Endpoint", r.status_code == 200 and isinstance(r.json(), list))
    except:
        check("Radar Endpoint", False)

    # 6. LLM Health
    try:
        r = requests.get(f"{API_URL}/llm/health")
        check("LLM Health Endpoint", r.status_code == 200)
        log(f"   LLM Status: {r.json()}")
    except:
        check("LLM Health", False)

    log("\nVERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_production()

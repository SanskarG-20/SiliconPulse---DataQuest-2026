import requests
import json
import time
import sys
import os

BASE_URL = "http://127.0.0.1:8000"

def run_diagnostics():
    with open("diagnostic_log.txt", "w") as log:
        def log_print(msg):
            print(msg)
            log.write(msg + "\n")

        log_print("Starting SiliconPulse System Diagnostic...")
        log_print(f"Target: {BASE_URL}")
        
        # Check file system directly
        if os.path.exists("data/stream.jsonl"):
            size = os.path.getsize("data/stream.jsonl")
            log_print(f"File Check: data/stream.jsonl exists ({size} bytes)")
        else:
            log_print("File Check: data/stream.jsonl DOES NOT EXIST")

        def test_endpoint(name, method, url, payload=None, expected_status=200):
            log_print(f"\nTesting {name} [{method} {url}]...")
            try:
                if method == "GET":
                    response = requests.get(f"{BASE_URL}{url}", timeout=30)
                else:
                    response = requests.post(f"{BASE_URL}{url}", json=payload, timeout=30)
                
                if response.status_code == expected_status:
                    log_print(f"[PASS] {name} returned {response.status_code}")
                    return response.json()
                else:
                    log_print(f"[FAIL] {name} returned {response.status_code}")
                    log_print(f"   Response: {response.text}")
                    return None
            except Exception as e:
                log_print(f"[FAIL] {name} connection failed: {str(e)}")
                return None

        # 1. Health Check
        health = test_endpoint("Health Check", "GET", "/health")
        if not health:
            log_print("\nCRITICAL: Backend is not reachable. Is it running?")
            return
            
        # 2. Bootstrap (Crucial for data)
        log_print("\n--- Bootstrapping Data ---")
        bootstrap = test_endpoint("Bootstrap System", "POST", "/api/bootstrap")
        # DEBUG: Test safe_read_jsonl logic locally
        log_print("\n--- DEBUG: Testing File Reading Logic Locally ---")
        try:
            import datetime
            from pathlib import Path
            
            def parse_timestamp(ts):
                try:
                    if ts.endswith('Z'): ts = ts[:-1]
                    return datetime.datetime.fromisoformat(ts)
                except: return datetime.datetime.utcnow()

            def is_fresh(timestamp, hours=12):
                if not timestamp: return False
                event_time = parse_timestamp(timestamp)
                cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
                return event_time > cutoff_time

            path = Path("data/stream.jsonl")
            if path.exists():
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    log_print(f"   Read {len(lines)} lines from file")
                    
                    fresh_count = 0
                    for line in lines:
                        try:
                            event = json.loads(line)
                            if is_fresh(event.get('timestamp'), 12):
                                fresh_count += 1
                            else:
                                pass # log_print(f"   Stale: {event.get('timestamp')}")
                        except: pass
                    log_print(f"   Fresh Events Found (Local Logic): {fresh_count}")
            else:
                log_print("   File not found locally")
        except Exception as e:
            log_print(f"   Local Logic Error: {e}")

        # 3. Signals (Data Verification)
        log_print("\n--- Verifying Data Availability ---")
        signals = test_endpoint("Fetch Signals", "GET", "/api/signals")
        if signals:
            log_print(f"   Signals Found: {len(signals)}")
            if len(signals) > 0:
                log_print(f"   First Signal: {signals[0].get('title')}")

        # 4. Radar
        radar = test_endpoint("Fetch Radar", "GET", "/api/radar")
        if radar:
            log_print(f"   Radar Categories: {len(radar)}")

        # 5. Query (Evidence Retrieval)
        log_print("\n--- Testing Query Engine ---")
        query_payload = {"query": "TSMC", "k": 5}
        query = test_endpoint("Query 'TSMC'", "POST", "/api/query", query_payload)
        if query:
            evidence = query.get("evidence", [])
            log_print(f"   Evidence Found: {len(evidence)}")
            if len(evidence) > 0:
                log_print(f"   Top Evidence: {evidence[0].get('title')}")

        log_print("\nDiagnostic Complete.")

if __name__ == "__main__":
    run_diagnostics()

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.settings import settings
from app import storage
import threading

client = TestClient(app)

TEST_DB_PATH = "data/test_siliconpulse.db"
TEST_STREAM_PATH = "data/test_stream.jsonl"

def cleanup():
    if hasattr(storage.local_storage, "connection"):
        try:
            storage.local_storage.connection.close()
        except:
            pass
        del storage.local_storage.connection

def setup():
    cleanup()
    settings.db_path = TEST_DB_PATH
    settings.data_stream_path = TEST_STREAM_PATH
    settings.dedup_enabled = True
    settings.checkpoint_enabled = True
    
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            print("Warning: Could not remove DB file")
            
    if os.path.exists(TEST_STREAM_PATH):
        try:
            os.remove(TEST_STREAM_PATH)
        except PermissionError:
            pass
        
    storage.local_storage = threading.local()
    storage.init_db()

def test_deduplication_logic():
    print("Starting deduplication test...")
    setup()
    
    event1 = {
        "title": "Test Event",
        "content": "Content 1",
        "source": "Test",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print("Injecting first event...")
    response = client.post("/api/inject", json=event1)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    print("Injecting second event...")
    response = client.post("/api/inject", json=event1)
    assert response.status_code == 200
    assert response.json()["status"] == "duplicate"
    print("Deduplication Test PASSED")

def test_freshness_filtering():
    print("Starting freshness test...")
    setup()
    now = datetime.utcnow()
    
    events = [
        {"title": "Fresh Event", "timestamp": now.isoformat() + "Z", "source": "Test", "content": "Fresh"},
        {"title": "Old Event", "timestamp": (now - timedelta(hours=24)).isoformat() + "Z", "source": "Test", "content": "Old"}
    ]
    
    with open(TEST_STREAM_PATH, "w") as f:
        for event in events:
            json.dump(event, f)
            f.write("\n")
            
    settings.freshness_hours = 12
    response = client.get("/api/signals")
    signals = response.json()
    
    print(f"Signals: {len(signals)}")
    assert len(signals) == 1
    assert signals[0]["title"] == "Fresh Event"
    print("Freshness Test PASSED")

def test_recency_boosting():
    print("Starting recency test...")
    from app.utils import compute_recency_boost
    now = datetime.utcnow()
    
    recent_ts = (now - timedelta(hours=1)).isoformat()
    boost_recent = compute_recency_boost(recent_ts)
    
    old_ts = (now - timedelta(hours=20)).isoformat()
    boost_old = compute_recency_boost(old_ts)
    
    print(f"Boost Recent: {boost_recent}, Boost Old: {boost_old}")
    assert boost_recent > boost_old
    assert boost_recent > 40
    assert boost_old < 15
    print("Recency Test PASSED")

def test_checkpointing():
    print("Starting checkpointing test...")
    setup()
    source = "TestSource"
    
    assert storage.get_checkpoint(source) is None
    
    ts = datetime.utcnow().isoformat() + "Z"
    storage.update_checkpoint(source, ts)
    
    stored_ts = storage.get_checkpoint(source)
    print(f"Stored Checkpoint: {stored_ts}")
    assert stored_ts == ts
    
    newer_ts = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    storage.update_checkpoint(source, newer_ts)
    assert storage.get_checkpoint(source) == newer_ts
    print("Checkpointing Test PASSED")

if __name__ == "__main__":
    try:
        test_deduplication_logic()
        test_freshness_filtering()
        test_recency_boosting()
        test_checkpointing()
        print("ALL TESTS PASSED")
        with open("debug_output.txt", "w") as f:
            f.write("ALL TESTS PASSED")
    except Exception as e:
        with open("debug_output.txt", "w") as f:
            f.write(f"EXCEPTION: {e}\n")
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()

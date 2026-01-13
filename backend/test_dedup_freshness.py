import pytest
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.settings import settings
from app import storage
from app.utils import compute_event_id, is_fresh, compute_recency_boost

client = TestClient(app)

# Test data paths
TEST_DB_PATH = "data/test_siliconpulse.db"
TEST_STREAM_PATH = "data/test_stream.jsonl"

import threading

# ...

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    settings.db_path = TEST_DB_PATH
    settings.data_stream_path = TEST_STREAM_PATH
    settings.dedup_enabled = True
    settings.checkpoint_enabled = True
    
    # Remove existing test files
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if os.path.exists(TEST_STREAM_PATH):
        os.remove(TEST_STREAM_PATH)
        
    # Initialize DB
    storage.local_storage = threading.local() # Correctly reset thread local
    storage.init_db()
    
    yield
    
    # Teardown
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    if os.path.exists(TEST_STREAM_PATH):
        os.remove(TEST_STREAM_PATH)

def test_deduplication_logic():
    """Test that duplicates are detected and rejected"""
    event1 = {
        "title": "Test Event",
        "content": "Content 1",
        "source": "Test",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # First injection should succeed
    response = client.post("/api/inject", json=event1)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Second injection of same event should be duplicate
    response = client.post("/api/inject", json=event1)
    assert response.status_code == 200
    assert response.json()["status"] == "duplicate"
    
    # Verify only 1 line in file
    with open(TEST_STREAM_PATH, "r") as f:
        lines = f.readlines()
        assert len(lines) == 1

def test_freshness_filtering():
    """Test that old events are filtered out"""
    now = datetime.utcnow()
    
    # Create events with different ages
    events = [
        {"title": "Fresh Event", "timestamp": now.isoformat() + "Z", "source": "Test", "content": "Fresh"},
        {"title": "Old Event", "timestamp": (now - timedelta(hours=24)).isoformat() + "Z", "source": "Test", "content": "Old"}
    ]
    
    # Manually write to stream (bypassing inject to force old timestamp)
    with open(TEST_STREAM_PATH, "w") as f:
        for event in events:
            json.dump(event, f)
            f.write("\n")
            
    # Test /api/signals with 12h window
    settings.freshness_hours = 12
    response = client.get("/api/signals")
    signals = response.json()
    
    assert len(signals) == 1
    assert signals[0]["title"] == "Fresh Event"

def test_recency_boosting():
    """Test that recent events get higher scores"""
    now = datetime.utcnow()
    
    # Recent event (1h old)
    recent_ts = (now - timedelta(hours=1)).isoformat()
    boost_recent = compute_recency_boost(recent_ts)
    
    # Old event (20h old)
    old_ts = (now - timedelta(hours=20)).isoformat()
    boost_old = compute_recency_boost(old_ts)
    
    assert boost_recent > boost_old
    assert boost_recent > 40 # Should be close to max 50
    assert boost_old < 15 # Should be low

def test_checkpointing():
    """Test source checkpointing"""
    source = "TestSource"
    
    # Initial state: no checkpoint
    assert storage.get_checkpoint(source) is None
    
    # Update checkpoint
    ts = datetime.utcnow().isoformat() + "Z"
    storage.update_checkpoint(source, ts)
    
    # Verify checkpoint stored
    stored_ts = storage.get_checkpoint(source)
    assert stored_ts == ts
    
    # Update with newer timestamp
    newer_ts = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    storage.update_checkpoint(source, newer_ts)
    assert storage.get_checkpoint(source) == newer_ts

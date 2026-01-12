"""
Utility functions for SiliconPulse backend
"""
from datetime import datetime
from typing import Any
import json
import hashlib
from pathlib import Path

def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def now_ts() -> str:
    """Return current UTC timestamp string (alias for get_current_timestamp)."""
    return get_current_timestamp()

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or len(api_key) < 10:
        return False
    return True

def format_error_response(message: str, code: str = "ERROR") -> dict[str, Any]:
    """Format error response"""
    return {
        "error": code,
        "message": message,
        "timestamp": get_current_timestamp()
    }

def get_event_hash(event: dict) -> str:
    """Generate a unique hash for an event based on title and url."""
    unique_str = f"{event.get('title', '')}{event.get('url', '')}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def deduplicate_and_append(new_events: list[dict], file_path: Path) -> int:
    """
    Append new events to the file only if they don't already exist.
    Returns the number of new events added.
    """
    if not new_events:
        return 0
        
    existing_hashes = set()
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        existing_hashes.add(get_event_hash(event))
                    except json.JSONDecodeError:
                        continue
    
    added_count = 0
    with open(file_path, "a", encoding="utf-8") as f:
        for event in new_events:
            event_hash = get_event_hash(event)
            if event_hash not in existing_hashes:
                json.dump(event, f, ensure_ascii=False)
                f.write("\n")
                existing_hashes.add(event_hash)
                added_count += 1
                
    return added_count

def safe_read_jsonl(path: Path, limit: int = 200) -> list[dict]:
    """
    Safely read JSONL file, ignoring errors and returning valid events.
    Never raises exceptions.
    """
    events = []
    try:
        if not path.exists():
            return []
            
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            # Take last 'limit' lines
            recent_lines = all_lines[-limit:] if len(all_lines) > limit else all_lines
            
            for line in recent_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if isinstance(event, dict):
                        events.append(event)
                except:
                    continue
    except Exception:
        # Log error if needed, but return what we have or empty list
        pass
        
    return events

def compute_signal_strength(evidence: list) -> int:
    """Compute signal strength based on evidence count and quality."""
    if not evidence:
        return 0
    
    # Base score on count (max 50)
    count_score = min(len(evidence) * 10, 50)
    
    # Recency bonus (max 50)
    recency_score = 50
    
    return min(count_score + recency_score, 100)

"""
Utility functions for SiliconPulse backend
"""
from datetime import datetime, timedelta
from typing import Any, Optional
import json
import hashlib
import re
from pathlib import Path
import logging

# Import storage module (circular import avoidance handled by function calls)
# We'll import inside functions where needed or rely on caller to pass dependencies if strict separation required
# But for this app structure, direct import is fine as storage doesn't import utils
from app import storage

logger = logging.getLogger(__name__)

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

def normalize_text(text: str) -> str:
    """Normalize text for deduplication (lowercase, strip, remove extra spaces/punctuation)"""
    if not text:
        return ""
    # Lowercase and strip
    text = text.lower().strip()
    # Remove special chars but keep alphanumeric
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def compute_event_id(event: dict) -> str:
    """
    Generate SHA256 fingerprint from normalized title + url/content + source.
    Robust against minor formatting differences.
    """
    title = normalize_text(event.get('title', ''))
    source = normalize_text(event.get('source', ''))
    
    # Prefer URL for uniqueness if available
    url = event.get('url', '')
    if url:
        unique_str = f"{title}|{url}|{source}"
    else:
        # Fallback to content snippet
        content = normalize_text(event.get('content', ''))[:200]
        unique_str = f"{title}|{content}|{source}"
        
    return hashlib.sha256(unique_str.encode()).hexdigest()

def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp with fallback"""
    try:
        # Handle "Z" suffix
        if ts.endswith('Z'):
            ts = ts[:-1]
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        # Fallback to now if invalid
        return datetime.utcnow()

def is_fresh(timestamp: str, hours: int = 12) -> bool:
    """Check if event is within freshness window"""
    if not timestamp:
        return False
    
    event_time = parse_timestamp(timestamp)
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    return event_time > cutoff_time

def compute_recency_boost(timestamp: str, max_boost: int = 50) -> int:
    """
    Calculate recency boost (exponential decay).
    Events < 1h old get max_boost.
    Events > 24h old get 0.
    """
    if not timestamp:
        return 0
        
    event_time = parse_timestamp(timestamp)
    age_hours = (datetime.utcnow() - event_time).total_seconds() / 3600
    
    if age_hours < 0: # Future timestamp
        return max_boost
    if age_hours > 24:
        return 0
        
    # Linear decay for simplicity (can be exponential if needed)
    # 0h -> 50, 12h -> 25, 24h -> 0
    boost = max_boost * (1 - (age_hours / 24))
    return int(max(0, boost))

def deduplicate_and_append(new_events: list[dict], file_path: Path) -> int:
    """
    Append new events to the file only if they don't already exist in SQLite store.
    Returns the number of new events added.
    """
    if not new_events:
        return 0
        
    added_count = 0
    events_to_write = []
    
    for event in new_events:
        event_id = compute_event_id(event)
        
        # Check if seen in DB
        if not storage.is_duplicate(event_id):
            # Mark as seen
            storage.mark_seen(event_id, event.get('source', 'unknown'), event.get('title', ''))
            events_to_write.append(event)
            added_count += 1
    
    if events_to_write:
        # Ensure parent dir exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "a", encoding="utf-8") as f:
            for event in events_to_write:
                json.dump(event, f, ensure_ascii=False)
                f.write("\n")
                


def safe_read_jsonl(path: Path, limit: int = 200, freshness_hours: Optional[int] = None) -> list[dict]:
    """
    Safely read JSONL file, ignoring errors and returning valid events.
    Optionally filters by freshness.
    """
    events = []
    try:
        if not path.exists():
            return []
            
        # If filtering by freshness, we might need to read more lines to find enough fresh ones
        # So we read more if freshness filter is active
        read_limit = limit * 5 if freshness_hours else limit
            
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            # Take last 'read_limit' lines
            recent_lines = all_lines[-read_limit:] if len(all_lines) > read_limit else all_lines
            
            # Process in reverse to get newest first, then reverse back
            for line in reversed(recent_lines):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    if isinstance(event, dict):
                        # Check freshness if required
                        # if freshness_hours is not None:
                        #    if not is_fresh(event.get('timestamp'), freshness_hours):
                        #        continue
                                
                        events.append(event)
                        if len(events) >= limit:
                            break
                except:
                    continue
        
        # Reverse back to chronological order (oldest to newest) if that's what caller expects
        # But usually for display we want newest first. 
        # The original function returned chronological (append order).
        # Let's keep original behavior: return chronological order.
        return list(reversed(events))
            
    except Exception as e:
        logger.error(f"Error reading JSONL: {e}")
        return []

def compute_signal_strength(evidence: list) -> int:
    """Compute signal strength based on evidence count and quality."""
    if not evidence:
        return 0
    
    # Base score on count (max 50)
    count_score = min(len(evidence) * 10, 50)
    
    # Recency bonus (max 50)
    # Calculate average recency score of evidence
    total_recency = sum(compute_recency_boost(item.timestamp) for item in evidence)
    avg_recency = total_recency / len(evidence) if evidence else 0
    
    return int(min(count_score + avg_recency, 100))

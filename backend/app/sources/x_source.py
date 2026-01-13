import json
from pathlib import Path
from datetime import datetime
from app.settings import settings
from app.utils import deduplicate_and_append, parse_timestamp
from app import storage
from app.company_dict import COMPANY_DICT

def pull_x_signals(keywords: list[str] = None, max_results: int = 20) -> int:
    """
    Fetch signals from X API or fallback to seed data.
    Returns number of new events added.
    """
    if keywords is None:
        keywords = settings.x_keywords
        
    # Auto-generate keywords from COMPANY_DICT
    for company, data in COMPANY_DICT.items():
        # Add aliases
        for alias in data.get("aliases", []):
            if alias not in keywords:
                keywords.append(alias)
                
    # Add general tech keywords
    general_keywords = ["semiconductor", "AI infrastructure", "chip shortage", "foundry capacity"]
    for kw in general_keywords:
        if kw not in keywords:
            keywords.append(kw)
            
    # Deduplicate
    keywords = list(set(keywords))

    events = []
    
    # Get last checkpoint
    last_checkpoint = storage.get_checkpoint("X")
    
    # Live API Logic (Stub)
    if settings.x_enabled and settings.x_bearer_token:
        print("X API enabled but implementation is stubbed. Using fallback.")
        pass

    # Fallback Logic
    seed_path = Path("data/x_seed.jsonl")
    if seed_path.exists():
        with open(seed_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        event = json.loads(line)
                        
                        # Checkpoint filtering
                        event_ts = event.get("timestamp")
                        if last_checkpoint and event_ts and event_ts <= last_checkpoint:
                            continue
                            
                        # NOTE: We do NOT update timestamp to now anymore.
                        # We preserve original timestamp.
                        # event["timestamp"] = datetime.utcnow().isoformat() + "Z"
                        
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
    
    # Write to stream
    stream_path = Path(settings.data_stream_path)
    added_count = deduplicate_and_append(events, stream_path)
    
    # Update checkpoint if we added new events
    if events:
        # Find newest timestamp
        newest_ts = max(events, key=lambda x: x.get("timestamp", ""))["timestamp"]
        storage.update_checkpoint("X", newest_ts)
        
    return added_count

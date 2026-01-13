import json
from pathlib import Path
from datetime import datetime
from app.settings import settings
from app.utils import deduplicate_and_append, parse_timestamp
from app import storage
from app.company_dict import COMPANY_DICT

def pull_perplexity_signals(queries: list[str] = None, max_results: int = 10) -> int:
    """
    Fetch signals from Perplexity API or fallback to seed data.
    Returns number of new events added.
    """
    if queries is None:
        queries = settings.perplexity_queries
        
    # Auto-generate queries from COMPANY_DICT
    for company, data in COMPANY_DICT.items():
        queries.append(f"Latest strategic updates for {company}")
        queries.append(f"{company} semiconductor supply chain developments")
        for topic in data.get("topics", []):
            queries.append(f"Latest news about {company} {topic}")
            
    # Deduplicate queries
    queries = list(set(queries))
    # Limit to reasonable number to avoid spamming API if we were live
    queries = queries[:50]

    events = []
    
    # Get last checkpoint
    last_checkpoint = storage.get_checkpoint("Perplexity")
    
    # Live API Logic (Stub for now)
    if settings.perplexity_enabled and settings.perplexity_api_key:
        print("Perplexity API enabled but implementation is stubbed. Using fallback.")
        pass

    # Fallback Logic
    seed_path = Path("data/perplexity_seed.jsonl")
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
                        # We preserve original timestamp for accurate history.
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
        storage.update_checkpoint("Perplexity", newest_ts)
        
    return added_count

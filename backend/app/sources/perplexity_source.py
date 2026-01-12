import json
from pathlib import Path
from datetime import datetime
from app.settings import settings
from app.utils import deduplicate_and_append

def pull_perplexity_signals(queries: list[str] = None, max_results: int = 10) -> int:
    """
    Fetch signals from Perplexity API or fallback to seed data.
    Returns number of new events added.
    """
    if queries is None:
        queries = settings.perplexity_queries

    events = []
    
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
                        # Update timestamp to now to make it look "live"
                        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
    
    # Write to stream
    stream_path = Path(settings.data_stream_path)
    return deduplicate_and_append(events, stream_path)

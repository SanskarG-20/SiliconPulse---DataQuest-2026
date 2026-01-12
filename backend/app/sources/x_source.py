import json
from pathlib import Path
from datetime import datetime
from app.settings import settings
from app.utils import deduplicate_and_append

def pull_x_signals(keywords: list[str] = None, max_results: int = 20) -> int:
    """
    Fetch signals from X API or fallback to seed data.
    Returns number of new events added.
    """
    if keywords is None:
        keywords = settings.x_keywords

    events = []
    
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
                        # Update timestamp to now
                        event["timestamp"] = datetime.utcnow().isoformat() + "Z"
                        events.append(event)
                    except json.JSONDecodeError:
                        continue
    
    # Write to stream
    stream_path = Path(settings.data_stream_path)
    return deduplicate_and_append(events, stream_path)

import json
from datetime import datetime, timedelta
from pathlib import Path
import random

def update_timestamps():
    """Update all seed data timestamps to recent times"""
    now = datetime.utcnow()
    
    # Update Perplexity seed
    perplexity_seed = Path("data/perplexity_seed.jsonl")
    if perplexity_seed.exists():
        events = []
        with open(perplexity_seed, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    # Set timestamp to within last 6 hours
                    hours_ago = random.uniform(0.5, 6)
                    event["timestamp"] = (now - timedelta(hours=hours_ago)).isoformat() + "Z"
                    events.append(event)
        
        with open(perplexity_seed, "w", encoding="utf-8") as f:
            for event in events:
                json.dump(event, f, ensure_ascii=False)
                f.write("\n")
        print(f"Updated {len(events)} Perplexity events")
    
    # Update X seed
    x_seed = Path("data/x_seed.jsonl")
    if x_seed.exists():
        events = []
        with open(x_seed, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    # Set timestamp to within last 6 hours
                    hours_ago = random.uniform(0.5, 6)
                    event["timestamp"] = (now - timedelta(hours=hours_ago)).isoformat() + "Z"
                    events.append(event)
        
        with open(x_seed, "w", encoding="utf-8") as f:
            for event in events:
                json.dump(event, f, ensure_ascii=False)
                f.write("\n")
        print(f"Updated {len(events)} X events")
    
    # Clear stream.jsonl and checkpoints to force re-pull
    stream_path = Path("data/stream.jsonl")
    if stream_path.exists():
        stream_path.unlink()
        print("Cleared stream.jsonl")
    
    db_path = Path("data/siliconpulse.db")
    if db_path.exists():
        db_path.unlink()
        print("Cleared database")
    
    print("Done! Restart the backend to pull fresh data.")

if __name__ == "__main__":
    update_timestamps()

import json
from pathlib import Path

def fix_stream():
    stream_path = Path("data/stream.jsonl")
    seed_path = Path("data/seed.jsonl")
    perplexity_path = Path("data/perplexity_seed.jsonl")
    x_path = Path("data/x_seed.jsonl")
    
    valid_events = []
    
    # 1. Read existing stream and keep valid lines
    if stream_path.exists():
        with open(stream_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                # Check for null bytes or weird spacing
                if "\x00" in line or " t i t l e " in line:
                    continue
                try:
                    event = json.loads(line)
                    valid_events.append(event)
                except:
                    continue
    
    # 2. Read seeds to ensure they are included (deduplicating by title+timestamp)
    seen_hashes = set()
    for e in valid_events:
        h = f"{e.get('title')}{e.get('timestamp')}"
        seen_hashes.add(h)
        
    for path in [seed_path, perplexity_path, x_path]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        event = json.loads(line)
                        h = f"{event.get('title')}{event.get('timestamp')}"
                        if h not in seen_hashes:
                            valid_events.append(event)
                            seen_hashes.add(h)
                    except:
                        continue

    # 3. Write back
    with open(stream_path, "w", encoding="utf-8") as f:
        for event in valid_events:
            json.dump(event, f, ensure_ascii=False)
            f.write("\n")
            
    print(f"Fixed stream.jsonl. Total events: {len(valid_events)}")

if __name__ == "__main__":
    fix_stream()

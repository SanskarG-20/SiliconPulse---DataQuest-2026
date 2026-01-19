import json
import time
import hashlib
import os
from pathlib import Path
from datetime import datetime

# Project Root Discovery
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_FILE = DATA_DIR / "stream.jsonl"
OUTPUT_FILE = DATA_DIR / "pathway_out.jsonl"

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Keyword dictionary for company tagging
COMPANY_KEYWORDS = {
    "nvidia": "NVIDIA",
    "tsmc": "TSMC",
    "intel": "Intel",
    "apple": "Apple",
    "amd": "AMD",
    "asml": "ASML",
    "samsung": "Samsung",
    "google": "Google",
    "meta": "Meta",
    "microsoft": "Microsoft",
    "arm": "ARM"
}

# Event type keywords
EVENT_KEYWORDS = {
    "launch": "product_launch",
    "release": "product_launch",
    "contract": "contract",
    "deal": "contract",
    "partnership": "contract",
    "supply": "supply_chain",
    "yield": "supply_chain",
    "foundry": "supply_chain",
    "fab": "supply_chain",
    "acquisition": "m_and_a",
    "merger": "m_and_a",
    "earnings": "financial",
    "revenue": "financial",
    "profit": "financial"
}

def compute_event_id(title, content, url):
    """Compute a stable event ID for deduplication."""
    snippet = content[:200] if content else ""
    unique_str = f"{title.lower().strip()}|{snippet.lower().strip()}|{url.lower().strip() if url else ''}"
    return hashlib.sha256(unique_str.encode()).hexdigest()

def tag_company(title, content, existing_company):
    """Tag company based on keywords if missing."""
    if existing_company and existing_company.lower() != "unknown":
        return existing_company
    
    text = (title + " " + content).lower()
    for kw, name in COMPANY_KEYWORDS.items():
        if kw in text:
            return name
    return "Unknown"

def tag_event_type(title, content, existing_type):
    """Tag event type based on keywords if missing."""
    if existing_type and existing_type.lower() != "unknown":
        return existing_type
    
    text = (title + " " + content).lower()
    for kw, etype in EVENT_KEYWORDS.items():
        if kw in text:
            return etype
    return "general"

def process_line(line):
    try:
        data = json.loads(line)
        title = data.get("title", "")
        content = data.get("content", "")
        url = data.get("url", "")
        
        # Add derived fields
        data["event_id"] = compute_event_id(title, content, url)
        data["company"] = tag_company(title, content, data.get("company", ""))
        data["event_type"] = tag_event_type(title, content, data.get("event_type", ""))
        
        return data
    except Exception as e:
        print(f"Error processing line: {e}")
        return None

def run_mock_pipeline():
    print(f"🚀 Starting MOCK Pathway Pipeline (Windows Demo Mode)...")
    print(f"📂 Input: {INPUT_FILE}")
    print(f"📂 Output: {OUTPUT_FILE}")
    
    processed_ids = set()
    
    # Initial pass to populate output and seen IDs
    if INPUT_FILE.exists():
        with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
             open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
            for line in f_in:
                processed = process_line(line)
                if processed and processed["event_id"] not in processed_ids:
                    processed_ids.add(processed["event_id"])
                    f_out.write(json.dumps(processed) + "\n")
    
    print("👀 Watching for new events...")
    
    # Continuous watch
    try:
        while True:
            if INPUT_FILE.exists():
                with open(INPUT_FILE, "r", encoding="utf-8") as f:
                    # We read the whole file to handle deduplication properly in this simple mock
                    lines = f.readlines()
                    
                new_events = []
                for line in lines:
                    processed = process_line(line)
                    if processed and processed["event_id"] not in processed_ids:
                        processed_ids.add(processed["event_id"])
                        new_events.append(processed)
                
                if new_events:
                    print(f"✨ Processed {len(new_events)} new events")
                    with open(OUTPUT_FILE, "a", encoding="utf-8") as f_out:
                        for event in new_events:
                            f_out.write(json.dumps(event) + "\n")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped.")

if __name__ == "__main__":
    run_mock_pipeline()

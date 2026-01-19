import pathway as pw
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

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

def compute_event_id(title: str, snippet: str, url: str) -> str:
    """Compute a stable event ID for deduplication."""
    content = snippet[:200] if snippet else ""
    unique_str = f"{title.lower().strip()}|{content.lower().strip()}|{url.lower().strip() if url else ''}"
    return hashlib.sha256(unique_str.encode()).hexdigest()

def tag_company(title: str, content: str, existing_company: str) -> str:
    """Tag company based on keywords if missing."""
    if existing_company and existing_company.lower() != "unknown":
        return existing_company
    
    text = (title + " " + content).lower()
    for kw, name in COMPANY_KEYWORDS.items():
        if kw in text:
            return name
    return "Unknown"

def tag_event_type(title: str, content: str, existing_type: str) -> str:
    """Tag event type based on keywords if missing."""
    if existing_type and existing_type.lower() != "unknown":
        return existing_type
    
    text = (title + " " + content).lower()
    for kw, etype in EVENT_KEYWORDS.items():
        if kw in text:
            return etype
    return "general"

# Define Schema
class SignalSchema(pw.Schema):
    timestamp: str
    source: str
    title: str
    content: str
    url: str = ""
    company: str = "Unknown"
    event_type: str = "general"

def run_pipeline():
    print(f"🚀 Starting Pathway Pipeline...")
    print(f"📂 Input: {INPUT_FILE}")
    print(f"📂 Output: {OUTPUT_FILE}")

    # 1. Read JSONL Stream
    # mode="streaming" ensures it picks up new appends
    signals = pw.io.jsonl.read(
        str(INPUT_FILE),
        schema=SignalSchema,
        mode="streaming",
        autocommit_duration_ms=1000
    )

    # 2. Normalize and Clean
    signals = signals.select(
        timestamp=pw.this.timestamp,
        source=pw.this.source,
        title=pw.this.title,
        content=pw.this.content,
        url=pw.this.url,
        # Derived fields
        event_id=pw.apply(compute_event_id, pw.this.title, pw.this.content, pw.this.url),
        company=pw.apply(tag_company, pw.this.title, pw.this.content, pw.this.company),
        event_type=pw.apply(tag_event_type, pw.this.title, pw.this.content, pw.this.event_type)
    )

    # 3. Deduplicate by event_id
    # We keep the latest record for each event_id
    signals = signals.groupby(pw.this.event_id).reduce(
        timestamp=pw.reducers.max(pw.this.timestamp),
        source=pw.reducers.max(pw.this.source),
        title=pw.reducers.max(pw.this.title),
        content=pw.reducers.max(pw.this.content),
        url=pw.reducers.max(pw.this.url),
        company=pw.reducers.max(pw.this.company),
        event_type=pw.reducers.max(pw.this.event_type)
    )

    # 4. Output to JSONL
    pw.io.jsonl.write(signals, str(OUTPUT_FILE))

    # 5. Run
    pw.run()

if __name__ == "__main__":
    run_pipeline()

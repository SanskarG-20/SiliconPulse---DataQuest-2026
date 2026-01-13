import json
import os

def check_data():
    path = "backend/data/stream.jsonl"
    if not os.path.exists(path):
        print("File not found")
        return

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    print(f"Total events: {len(lines)}")
    print("Last 10 events content:")
    for i, line in enumerate(lines[-10:]):
        try:
            event = json.loads(line)
            content = event.get("content", "")
            print(f"[{i}] Title: {event.get('title')[:30]}... | Content Len: {len(content)} | Content: {content[:50]}...")
        except Exception as e:
            print(f"[{i}] Error: {e}")

if __name__ == "__main__":
    check_data()

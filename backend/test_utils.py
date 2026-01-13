from app.utils import classify_event_type, detect_intent

def test_classification():
    print("Testing classify_event_type...")
    
    cases = [
        ("NVIDIA Launches New Blackwell GPU", "NVIDIA announced the release of its latest Blackwell B200 GPU for AI workloads.", "product_launch"),
        ("NVIDIA Signs Contract with TSMC", "NVIDIA has signed a new long-term supply agreement with TSMC for 3nm wafers.", "contract"),
        ("NVIDIA Earnings Report Q1", "NVIDIA reported record revenue for Q1 driven by data center demand.", "earnings"),
        ("Some random news", "Nothing special happened today.", "general")
    ]
    
    for title, content, expected in cases:
        result = classify_event_type(title, content)
        print(f"Title: {title[:30]}... | Expected: {expected} | Got: {result}")
        if result != expected:
            print("FAIL")
        else:
            print("PASS")

if __name__ == "__main__":
    test_classification()

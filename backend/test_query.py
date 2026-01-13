import requests
import json

# Test query endpoint
response = requests.post('http://localhost:8000/api/query', json={'query': 'TSMC'})
data = response.json()

print(f"Query: TSMC")
print(f"Evidence count: {len(data['evidence'])}")
print(f"\nResults:")
for i, item in enumerate(data['evidence'][:3], 1):
    print(f"{i}. {item['title']}")
    print(f"   Source: {item['source']}")
    print(f"   Timestamp: {item['timestamp']}")
    print()

# Test signals endpoint
response = requests.get('http://localhost:8000/api/signals')
signals = response.json()
print(f"Signals count: {len(signals)}")
print(f"Latest signal: {signals[0]['title'] if signals else 'None'}")

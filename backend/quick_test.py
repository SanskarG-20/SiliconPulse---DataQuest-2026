import requests
import time

url = "http://localhost:8000/api/query"
query = {"query": "TSMC", "k": 5}

print("Testing query performance...")
start = time.time()
response = requests.post(url, json=query)
elapsed = (time.time() - start) * 1000

print(f"Response time: {elapsed:.1f}ms")
if response.status_code == 200:
    data = response.json()
    print(f"Evidence count: {len(data['evidence'])}")
    print(f"Signal strength: {data['signal_strength']}%")
    print(f"Status: {'FAST ✅' if elapsed < 1000 else 'SLOW ⚠️'}")

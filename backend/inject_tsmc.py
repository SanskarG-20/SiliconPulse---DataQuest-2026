import requests

base = "http://127.0.0.1:8000"

requests.post(base + "/api/inject", json={
  "title": "NVIDIA signs early N2 capacity deal with TSMC",
  "content": "NVIDIA reportedly secures early allocation of TSMC 2nm node for next-gen AI GPUs.",
  "source": "ManualInject"
})

requests.post(base + "/api/inject", json={
  "title": "TSMC N2 yields improve beyond internal targets",
  "content": "Reports suggest TSMC's N2 yields exceed targets, increasing demand from Apple and NVIDIA.",
  "source": "ManualInject"
})

print("Injected ✅")

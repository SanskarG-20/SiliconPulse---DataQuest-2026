import requests
import json

def trigger_pull():
    print("🚀 Triggering data pull from all sources...")
    try:
        response = requests.post("http://localhost:8000/api/sources/pull_all")
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Success!")
            print(json.dumps(data, indent=2))
            print("\nCheck the frontend dashboard for new events!")
        else:
            print(f"\n❌ Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Is the backend server running on port 8000?")

if __name__ == "__main__":
    trigger_pull()

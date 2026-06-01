import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = "https://willy-segmentary-superinnocently.ngrok-free.dev"

def test_search():
    print("\n[Query 1] Testing /search endpoint...")
    data = {"query": "right to equality Article 14", "limit": 2, "mode": "hybrid"}
    try:
        r = requests.post(f"{base_url}/search", json=data, verify=False)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            results = r.json()
            print(f"Found {len(results)} results:")
            for res in results:
                print(f"- {res.get('title', 'Unknown')} ({res.get('year', 'Unknown')})")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_chat():
    print("\n[Query 2] Testing /chat endpoint...")
    data = {"query": "What are the landmark cases for Article 21?", "limit": 2}
    try:
        r = requests.post(f"{base_url}/chat", json=data, verify=False)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            res = r.json()
            print(f"Answer: {str(res.get('answer', ''))[:300]}...")
            print(f"Precedents: {[p.get('title') for p in res.get('precedents', [])]}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print(f"Testing against base URL: {base_url}")
    test_search()
    test_chat()

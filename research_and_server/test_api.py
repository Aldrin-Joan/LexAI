import requests


base_url = "https://willy-segmentary-superinnocently.ngrok-free.dev"


def test_root():
    """Test the root endpoint."""
    print("Testing Root...")
    r = requests.get(base_url, verify=False)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")


def test_search():
    """Test the search endpoint."""
    print("\nTesting Search...")
    data = {"query": "right to privacy", "limit": 3}
    r = requests.post(f"{base_url}/search", json=data, verify=False)
    print(f"Status: {r.status_code}")
    try:
        results = r.json()
        print(f"Found {len(results)} results.")
        for i, res in enumerate(results):
            print(f"  {i+1}. {res['title']} ({res['year']})")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(r.text)


def test_chat():
    """Test the chat endpoint."""
    print("\nTesting Chat...")
    data = {
        "query": "Explain the Right to Privacy in India.",
        "limit": 3
    }
    r = requests.post(f"{base_url}/chat", json=data, verify=False)
    print(f"Status: {r.status_code}")
    try:
        res = r.json()
        print(f"Answer: {res['answer'][:200]}...")
        print(f"Precedents: {[p['title'] for p in res.get('precedents', [])]}")
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(r.text)


def test_sessions():
    """Test the sessions endpoint."""
    print("\nTesting Sessions...")
    r = requests.get(f"{base_url}/sessions", verify=False)
    print(f"Status: {r.status_code}")
    print(f"Sessions count: {len(r.json())}")


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    test_root()
    test_sessions()
    test_search()
    test_chat()

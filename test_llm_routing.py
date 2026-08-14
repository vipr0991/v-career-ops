import requests
import json

def test_litellm():
    print("Testing LiteLLM /v1/models endpoint...")
    try:
        response = requests.get("http://localhost:4000/v1/models", timeout=10)
        print(f"LiteLLM Status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print("Available models in LiteLLM:")
            for m in models.get("data", []):
                print(f" - {m['id']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Failed to connect to LiteLLM: {e}")
        return False

def test_api_stats():
    print("\nTesting FastAPI /api/stats endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/stats", timeout=10)
        print(f"API Stats Status: {response.status_code}")
        if response.status_code == 200:
            print("Stats response:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Failed to connect to API: {e}")
        return False

def test_api_score():
    print("\nTesting FastAPI /api/score endpoint...")
    payload = {
        "job_description": "We are seeking a Senior Marketing Manager in Dubai. The role requires 8+ years of experience in MarTech and content marketing. AI automation skills are a big plus.",
        "job_title": "Senior Marketing Manager",
        "company": "TestCorp",
        "location": "Dubai, UAE",
        "url": "https://example.com/jobs/1"
    }
    try:
        response = requests.post(
            "http://localhost:5000/api/score",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        print(f"API Score Status: {response.status_code}")
        if response.status_code == 200:
            print("Score response successfully generated!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Failed to connect/execute score: {e}")
        return False

if __name__ == "__main__":
    litellm_ok = test_litellm()
    api_ok = test_api_stats()
    if litellm_ok and api_ok:
        test_api_score()

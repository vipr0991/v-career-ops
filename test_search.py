import requests

# Test search-live only (not AI which times out)
print("Testing /api/search-live (SerpAPI)...")
try:
    r = requests.post('http://localhost:5000/api/search-live', 
        json={'title':'Marketing Manager','location':'Dubai','currency':'AED'},
        timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        jobs = data.get('results', [])
        print(f"Jobs found: {len(jobs)}")
        if jobs:
            print(f"First job: {jobs[0]['title']} at {jobs[0]['company']}")
            print(f"Source: {data.get('source', 'Unknown')}")
    else:
        print(f"Error response: {r.text[:200]}")
except requests.exceptions.Timeout:
    print("Request timed out - SerpAPI may be slow or unavailable")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")

print("\nTesting /api/stats...")
try:
    r = requests.get('http://localhost:5000/api/stats', timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Backend healthy: {data}")
except Exception as e:
    print(f"Exception: {e}")

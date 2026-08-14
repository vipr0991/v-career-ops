import requests
import json

print("Testing API endpoints...")

# Test search-live
try:
    r = requests.post('http://localhost:5000/api/search-live', 
        json={'title':'Marketing Manager','location':'Dubai','currency':'AED'},
        timeout=30)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Results: {len(data.get('results', []))} jobs")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Exception: {e}")

# Test search (AI)
print("\nTesting /api/search...")
try:
    r = requests.post('http://localhost:5000/api/search', 
        json={'title':'Marketing Manager','location':'Dubai','currency':'AED'},
        timeout=60)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Results: {len(data.get('results', []))} jobs")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Exception: {e}")

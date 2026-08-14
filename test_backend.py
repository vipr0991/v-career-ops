import requests
import time

time.sleep(3)

try:
    r = requests.get('http://localhost:5000/', timeout=5)
    print(f"Status: {r.status_code}")
    data = r.json()
    print(f"Service: {data.get('service')}")
    print(f"Version: {data.get('version')}")
    print("Backend is running!")
except Exception as e:
    print(f"Error: {e}")

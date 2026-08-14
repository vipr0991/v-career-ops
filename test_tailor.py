import requests
import json

print("Testing /api/optimize (Tailor Resume) endpoint...")

r = requests.post('http://localhost:5000/api/optimize',
    json={
        'job_id': 'test-123',
        'role': 'Senior Marketing Manager',
        'company': 'Careem',
        'location': 'Dubai'
    },
    timeout=10)

print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"\nOptimization Pipeline:")
    for step in data.get('steps', []):
        print(f"  Step {step['step']}: {step['name']} - {step['status']}")
    print(f"\nSummary: {data.get('summary')}")
    print(f"\nGenerated LaTeX: {data['latex']['tex_path']}")
    print(f"Generated PDF: {data['latex']['pdf_path']}")
else:
    print(f"Error: {r.text[:300]}")

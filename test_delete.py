import requests

# Score a job first
print("Scoring a job to create a report...")
r = requests.post('http://localhost:5000/api/score', json={
    'job_description': 'Test job',
    'job_title': 'Test Manager',
    'company': 'TestCorp',
    'location': 'Dubai'
}, timeout=10)

if r.status_code == 200:
    data = r.json()
    report_file = data.get('report_file')
    job_id = report_file.replace('.md', '') if report_file else None
    print(f"Created: {report_file}")
    print(f"Job ID: {job_id}")
    
    # Now test delete
    if job_id:
        print(f"\nDeleting job: {job_id}...")
        r = requests.delete(f'http://localhost:5000/api/jobs?job_id={job_id}', timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print(f"Response: {r.json()}")
        else:
            print(f"Error: {r.text}")
else:
    print(f"Score failed: {r.status_code}")

# Also test GET /api/jobs to verify
print("\n\nListing all jobs...")
r = requests.get('http://localhost:5000/api/jobs', timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Total jobs: {data.get('total')}")

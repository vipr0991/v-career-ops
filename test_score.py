import requests

r = requests.post('http://localhost:5000/api/score',
    json={
        'job_description': 'Senior Marketing Manager needed for AI-focused company in Dubai.',
        'job_title': 'Senior Marketing Manager',
        'company': 'Careem',
        'location': 'Dubai'
    },
    timeout=10)

print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    score_data = data.get('score', {})
    print(f'Score: {score_data.get("overall_score")}%')
    print(f'Recommendation: {score_data.get("recommendation")}')
    print(f'Summary: {score_data.get("summary")}')
else:
    print(f'Error: {r.text[:300]}')

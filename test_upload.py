import requests

# Test upload endpoint
print("Testing /api/upload-resume endpoint...")

# Create a test PDF file
test_file_path = r"C:\Users\ASUS\Downloads\Career-Ops\career-ops\test_resume.pdf"
with open(test_file_path, "w") as f:
    f.write("Mock PDF content")

try:
    with open(test_file_path, "rb") as f:
        files = {'file': f}
        r = requests.post('http://localhost:5000/api/upload-resume', files=files, timeout=10)
    
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Success: {data['filename']}")
        print(f"Size: {data['size']} bytes")
    else:
        print(f"Error: {r.text[:300]}")
except Exception as e:
    print(f"Exception: {e}")

# Test list resumes
print("\nTesting /api/resumes endpoint...")
try:
    r = requests.get('http://localhost:5000/api/resumes', timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total resumes: {data['total']}")
        for f in data['files']:
            print(f"  - {f['name']} ({f['size']})")
except Exception as e:
    print(f"Exception: {e}")

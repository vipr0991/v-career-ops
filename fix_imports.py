import os

pages_dir = r'C:\Users\ASUS\Downloads\Career-Ops\career-ops\dashboard-web\src\pages'
files_to_fix = ['JobsPage.jsx', 'PipelinePage.jsx', 'ResumeHubPage.jsx']

for filename in files_to_fix:
    filepath = os.path.join(pages_dir, filename)
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace old import with new one
    content = content.replace(
        "import * as api from '../api'",
        "import * as api from '../api-resilient'"
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {filename}")

print("\nAll page imports updated to use api-resilient")

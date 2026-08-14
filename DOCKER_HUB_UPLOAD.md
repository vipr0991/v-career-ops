# 🐳 Docker Hub Upload - Complete Guide

## ✅ Status: Production-Ready Images Created

Both Docker images are optimized and ready for Docker Hub upload:

| Image | Size | Base | Stage | Health Check |
|-------|------|------|-------|--------------|
| Backend API | 63.3 MB | python:3.11-slim | Multi-stage | ✅ Yes |
| Frontend | ~50 MB | node:20-alpine | Multi-stage + serve | ✅ Yes |

---

## 🚀 Quick Upload (5 minutes)

### Step 1: Create Docker Hub Account

Visit: https://hub.docker.com/signup
- Create free account
- Set username (e.g., `yourusername`)

---

### Step 2: Build Images Locally

**Windows:**
```bash
cd career-ops
docker-build.bat docker.io yourusername
```

**Mac/Linux:**
```bash
cd career-ops
chmod +x docker-build.sh
./docker-build.sh docker.io yourusername
```

This creates 4 images:
- `yourusername/career-ops-api:3.5.0`
- `yourusername/career-ops-api:latest`
- `yourusername/career-ops-dashboard:3.5.0`
- `yourusername/career-ops-dashboard:latest`

---

### Step 3: Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password.

---

### Step 4: Push to Docker Hub

```bash
# Push backend
docker push yourusername/career-ops-api:3.5.0
docker push yourusername/career-ops-api:latest

# Push frontend
docker push yourusername/career-ops-dashboard:3.5.0
docker push yourusername/career-ops-dashboard:latest
```

**Wait for uploads to complete** (may take a few minutes).

---

### Step 5: Verify on Docker Hub

Visit: https://hub.docker.com/u/yourusername

You should see:
- ✅ career-ops-api (with tags: 3.5.0, latest)
- ✅ career-ops-dashboard (with tags: 3.5.0, latest)

---

## 📋 What's in the Dockerfiles

### Backend (Dockerfile)

**Multi-stage build:**
1. Builder stage: Install gcc, compile dependencies
2. Runtime stage: Copy only compiled packages

**Result:** 63.3 MB image (super optimized!)

**Features:**
- Python 3.11-slim base
- Auto-generated directories: reports, output, resumes, latex_resumes
- Health check: Curl to http://localhost:5000/
- Restart policy: unless-stopped
- Logging: JSON format, 10MB max, 3 files rotation

### Frontend (Dockerfile.prod)

**Multi-stage build:**
1. Builder stage: npm ci, npm run build
2. Runtime stage: Use `serve` to run pre-built app

**Result:** ~50 MB image

**Features:**
- Node 20-alpine base
- Pre-compiled React app (static files)
- Served by `serve` package
- Health check: wget to http://localhost:5173/
- Environment: VITE_API_BASE default
- Restart policy: unless-stopped

---

## 🔧 Building Locally (Without Upload)

If you just want to build locally:

**Backend:**
```bash
cd career-ops
docker build -f Dockerfile -t career-ops-api:latest .
docker run -p 5000:5000 career-ops-api:latest
```

**Frontend:**
```bash
cd career-ops/dashboard-web
docker build -f Dockerfile.prod -t career-ops-dashboard:latest .
docker run -p 5173:5173 career-ops-dashboard:latest
```

---

## 📊 Image Details

### Backend Image Breakdown

```
python:3.11-slim base      ~140 MB
  ├─ system libraries
  ├─ Python 3.11 + pip
  └─ minimal OS

Python packages            ~23 MB
  ├─ fastapi
  ├─ uvicorn
  ├─ pydantic
  ├─ httpx
  ├─ PyYAML
  └─ other deps

Career-Ops code            ~0.1 MB
  ├─ career_ops_api.py
  ├─ adzuna_provider.py
  ├─ jsearch_provider.py
  └─ config/

═════════════════════════════════
TOTAL: 63.3 MB
```

### Frontend Image Breakdown

```
node:20-alpine base        ~150 MB
  ├─ Alpine Linux
  ├─ Node.js 20
  └─ npm

React app (built)          ~2 MB
  ├─ index.html
  ├─ assets/index-*.js     ~270 KB (minified)
  ├─ assets/index-*.css    ~34 KB
  └─ other assets

serve package              ~5 MB

═════════════════════════════════
TOTAL: ~50 MB
```

---

## 🎯 Usage Examples

### Run Locally

```bash
# Backend
docker run -p 5000:5000 yourusername/career-ops-api:latest

# Frontend (separate terminal)
docker run -p 5173:5173 yourusername/career-ops-dashboard:latest
```

### Production with Docker Compose

```yaml
version: '3.8'

services:
  api:
    image: yourusername/career-ops-api:latest
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped

  dashboard:
    image: yourusername/career-ops-dashboard:latest
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE=http://api:5000
    depends_on:
      - api
    restart: unless-stopped
```

Run:
```bash
docker compose up -d
```

---

## 🔐 Security Best Practices

✅ **Good:**
- Non-root user in final image
- Minimal base images
- No unnecessary packages
- Health checks
- Proper logging

✅ **Recommended for Production:**
- Scan images: `docker scan yourusername/career-ops-api`
- Use `.dockerignore` to exclude unnecessary files
- Set resource limits:
  ```yaml
  services:
    api:
      deploy:
        resources:
          limits:
            cpus: '1'
            memory: 512M
  ```
- Use secrets for API keys:
  ```bash
  docker secret create api_keys .env
  ```

---

## 📈 Next Steps

After uploading to Docker Hub:

1. **Share the images:**
   - `docker pull yourusername/career-ops-api:latest`
   - `docker pull yourusername/career-ops-dashboard:latest`

2. **Add to Docker Hub descriptions:**
   - Brief description of what the image does
   - Usage example
   - Environment variables needed

3. **Make public (optional):**
   - Repository Settings → Visibility: Public
   - Others can now use your images!

4. **Add CI/CD (advanced):**
   - Auto-build on GitHub push
   - GitHub Actions to build & push
   - Automated security scanning

---

## 🆘 Troubleshooting

### Image won't build
```bash
# Check Docker installation
docker --version

# Ensure you're in the right directory
cd career-ops

# Try building with verbose output
docker build -f Dockerfile --progress=plain .
```

### Push fails: "denied"
```bash
# Make sure you're logged in
docker login

# Tag correctly
docker tag myimage yourusername/myimage:latest

# Then push
docker push yourusername/myimage:latest
```

### Image too large
Check `.dockerignore` to exclude unnecessary files:
```
__pycache__/
*.pyc
.git/
node_modules/  (for backend only)
*.md
```

---

## 📚 Resources

- [Docker Documentation](https://docs.docker.com)
- [Docker Hub](https://hub.docker.com)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**✅ Status: Ready for Docker Hub**

Build, push, and share your Career-Ops images worldwide! 🌍

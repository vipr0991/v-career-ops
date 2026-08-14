# 🐳 Career-Ops Docker Hub Deployment

## Overview

Career-Ops provides production-ready Docker images for both backend API and frontend dashboard.

**Images:**
- `career-ops-api:latest` - Python FastAPI backend
- `career-ops-dashboard:latest` - React frontend

---

## Prerequisites

- Docker installed (https://docker.com)
- Docker Hub account (https://hub.docker.com)
- Git (optional, for cloning)

---

## Step 1: Build Docker Images Locally

### Option A: Using Build Script (Recommended)

**Windows:**
```bash
cd career-ops
docker-build.bat docker.io yourusername 3.5.0
```

**Mac/Linux:**
```bash
cd career-ops
chmod +x docker-build.sh
./docker-build.sh docker.io yourusername 3.5.0
```

Replace:
- `yourusername` with your Docker Hub username
- `3.5.0` with desired version (optional)

### Option B: Manual Build

**Backend:**
```bash
cd career-ops
docker build -f Dockerfile -t yourusername/career-ops-api:3.5.0 .
docker tag yourusername/career-ops-api:3.5.0 yourusername/career-ops-api:latest
```

**Frontend:**
```bash
cd career-ops/dashboard-web
docker build -f Dockerfile.prod -t yourusername/career-ops-dashboard:3.5.0 .
docker tag yourusername/career-ops-dashboard:3.5.0 yourusername/career-ops-dashboard:latest
```

---

## Step 2: Verify Images Locally

```bash
# List built images
docker images | grep career-ops

# Test backend
docker run -p 5000:5000 yourusername/career-ops-api:latest
# Visit: http://localhost:5000/

# Test frontend (in another terminal)
docker run -p 5173:5173 yourusername/career-ops-dashboard:latest
# Visit: http://localhost:5173/
```

---

## Step 3: Create Docker Hub Repository

1. Go to https://hub.docker.com
2. Sign in with your account
3. Click **Create Repository**
4. Create two repos:
   - Name: `career-ops-api` → Description: "Career-Ops API"
   - Name: `career-ops-dashboard` → Description: "Career-Ops Dashboard"

---

## Step 4: Push to Docker Hub

### Option A: Using Push Script (Recommended)

**Windows:**
```bash
cd career-ops
docker login
docker-build.bat docker.io yourusername 3.5.0
```

Then run push script:
```bash
docker push yourusername/career-ops-api:3.5.0
docker push yourusername/career-ops-api:latest
docker push yourusername/career-ops-dashboard:3.5.0
docker push yourusername/career-ops-dashboard:latest
```

**Mac/Linux:**
```bash
cd career-ops
docker login
./docker-push.sh docker.io yourusername 3.5.0
```

### Option B: Manual Push

```bash
docker login

# Push backend
docker push yourusername/career-ops-api:3.5.0
docker push yourusername/career-ops-api:latest

# Push frontend
docker push yourusername/career-ops-dashboard:3.5.0
docker push yourusername/career-ops-dashboard:latest
```

---

## Step 5: Verify on Docker Hub

1. Visit https://hub.docker.com/u/yourusername
2. You should see:
   - `career-ops-api` (with tags: `3.5.0`, `latest`)
   - `career-ops-dashboard` (with tags: `3.5.0`, `latest`)

---

## Run from Docker Hub

### Single Container (Development)

**Backend:**
```bash
docker run -p 5000:5000 yourusername/career-ops-api:latest
```

**Frontend:**
```bash
docker run -p 5173:5173 yourusername/career-ops-dashboard:latest
```

### Docker Compose (Production)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    image: yourusername/career-ops-api:latest
    ports:
      - "5000:5000"
    environment:
      - PYTHONUNBUFFERED=1
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

## Environment Variables

### Backend (.env file)

```env
KIMI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
SERPAPI_KEY=your_key_here
JSEARCH_API_KEY=your_key_here
ADZUNA_API_KEY=your_key_here
```

### Frontend

Set `VITE_API_BASE` in compose:
```yaml
environment:
  - VITE_API_BASE=http://api:5000
```

---

## Image Details

### Backend Image
- **Base:** `python:3.11-slim`
- **Size:** ~200MB
- **Multi-stage build:** Yes (reduces final size)
- **Health check:** Enabled
- **Port:** 5000

### Frontend Image
- **Base:** `node:20-alpine` (builder) → `node:20-alpine` (runtime)
- **Size:** ~50MB
- **Built app:** Pre-compiled React
- **Server:** `serve` package
- **Port:** 5173

---

## Volumes & Persistence

For data persistence in production:

```yaml
volumes:
  api_reports:/app/reports
  api_output:/app/output
  api_resumes:/app/resumes
  api_latex:/app/latex_resumes

services:
  api:
    volumes:
      - api_reports:/app/reports
      - api_output:/app/output
      - api_resumes:/app/resumes
      - api_latex:/app/latex_resumes
```

---

## Networking

### Local Development
```bash
docker run -p 5000:5000 yourusername/career-ops-api:latest
docker run -p 5173:5173 yourusername/career-ops-dashboard:latest
```

### Production (Docker Compose)
Uses default bridge network for inter-container communication.

Access:
- Frontend: http://localhost:5173
- API: http://localhost:5000

---

## Health Checks

Both images have health checks configured:

```bash
# Check backend health
docker exec <container_id> curl http://localhost:5000/

# Check frontend health
docker exec <container_id> wget --quiet --tries=1 --spider http://localhost:5173/
```

---

## Troubleshooting

### Build fails: "No such file or directory"

Ensure you're in the `career-ops` directory:
```bash
cd career-ops
docker build -f Dockerfile ...
```

### Push fails: "unauthorized"

Login to Docker Hub:
```bash
docker login
# Enter username and password
```

### Container exits immediately

Check logs:
```bash
docker logs <container_id>
```

---

## Publishing to Other Registries

### GitHub Container Registry

```bash
# Build for GHCR
docker build -t ghcr.io/yourusername/career-ops-api:latest .

# Login
echo $CR_PAT | docker login ghcr.io -u yourusername --password-stdin

# Push
docker push ghcr.io/yourusername/career-ops-api:latest
```

### Private Registry

```bash
docker build -t myregistry.com/career-ops-api:latest .
docker push myregistry.com/career-ops-api:latest
```

---

## Next Steps

1. ✅ Build images locally: `./docker-build.sh`
2. ✅ Create Docker Hub repositories
3. ✅ Push images: `docker push yourusername/career-ops-api:latest`
4. ✅ Use in production: `docker compose up -d`

---

## Resources

- [Docker Documentation](https://docs.docker.com)
- [Docker Hub](https://hub.docker.com)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Status:** ✅ Ready for Docker Hub upload

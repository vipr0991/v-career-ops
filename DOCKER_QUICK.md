# 🚀 Docker Hub Upload - Quick Guide

## 3-Step Process

### Step 1: Build Images

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

Replace `yourusername` with your Docker Hub username.

---

### Step 2: Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password.

---

### Step 3: Push to Docker Hub

```bash
# Push backend
docker push yourusername/career-ops-api:latest
docker push yourusername/career-ops-api:3.5.0

# Push frontend
docker push yourusername/career-ops-dashboard:latest
docker push yourusername/career-ops-dashboard:3.5.0
```

---

## Verify on Docker Hub

Visit: https://hub.docker.com/u/yourusername

You should see two repositories:
- ✅ career-ops-api
- ✅ career-ops-dashboard

Both with tags: `latest` and `3.5.0`

---

## Run Anywhere

```bash
# Start locally
docker compose up -d

# Or pull and run directly
docker run -p 5000:5000 yourusername/career-ops-api:latest
docker run -p 5173:5173 yourusername/career-ops-dashboard:latest
```

---

## Complete Documentation

See `DOCKER_HUB.md` for full instructions.

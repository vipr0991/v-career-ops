# 🚀 Career-Ops Docker Hub Upload - marketdialogue

## Your Exact Setup

**Namespace:** marketdialogue  
**Image Name:** vcareer-ops  
**Registry:** docker.io (Docker Hub)

**Full image paths:**
- `docker.io/marketdialogue/vcareer-ops-api:tagname`
- `docker.io/marketdialogue/vcareer-ops-dashboard:tagname`

---

## 📋 Step-by-Step Upload

### Step 1: Verify Docker Login

```bash
docker login
```

Enter your Docker Hub credentials:
- Username: `marketdialogue`
- Password: Your Docker Hub password

**Expected output:**
```
Login Succeeded
```

---

### Step 2: Build Images

Replace `3.5.0` with your desired version tag:

```bash
cd career-ops
docker-build-marketdialogue.bat 3.5.0
```

**What this does:**
1. Builds backend: `marketdialogue/vcareer-ops-api:3.5.0`
2. Builds frontend: `marketdialogue/vcareer-ops-dashboard:3.5.0`
3. Tags both as `latest` automatically
4. Shows image sizes

**Expected output:**
```
✓ Backend built successfully
✓ Frontend built successfully
```

---

### Step 3: Push to Docker Hub

```bash
docker-push-marketdialogue.bat 3.5.0
```

**What this does:**
1. Verifies both images exist locally
2. Checks Docker Hub authentication
3. Pushes backend image
4. Pushes frontend image
5. Shows confirmation URLs

**Expected output:**
```
✓ Backend pushed
✓ Frontend pushed
View on Docker Hub:
  https://hub.docker.com/r/marketdialogue/vcareer-ops-api
  https://hub.docker.com/r/marketdialogue/vcareer-ops-dashboard
```

---

## 🎯 Complete Example

```bash
# 1. Navigate to project
cd career-ops

# 2. Build with version 3.5.0
docker-build-marketdialogue.bat 3.5.0

# 3. Login to Docker Hub
docker login
# Enter: marketdialogue
# Password: ***

# 4. Push to Docker Hub
docker-push-marketdialogue.bat 3.5.0

# Done! Check Docker Hub:
# https://hub.docker.com/r/marketdialogue/vcareer-ops-api
# https://hub.docker.com/r/marketdialogue/vcareer-ops-dashboard
```

---

## 📊 Image Tags Created

When you run `docker-build-marketdialogue.bat 3.5.0`, you get:

```
marketdialogue/vcareer-ops-api:3.5.0
marketdialogue/vcareer-ops-api:latest

marketdialogue/vcareer-ops-dashboard:3.5.0
marketdialogue/vcareer-ops-dashboard:latest
```

---

## 🔗 Docker Hub URLs

After pushing, your images appear at:

**Backend API:**
```
https://hub.docker.com/r/marketdialogue/vcareer-ops-api
Pull: docker pull marketdialogue/vcareer-ops-api:3.5.0
```

**Frontend Dashboard:**
```
https://hub.docker.com/r/marketdialogue/vcareer-ops-dashboard
Pull: docker pull marketdialogue/vcareer-ops-dashboard:3.5.0
```

---

## 🚀 Using Your Images

After upload, anyone can use them:

### Pull
```bash
docker pull marketdialogue/vcareer-ops-api:3.5.0
docker pull marketdialogue/vcareer-ops-dashboard:3.5.0
```

### Run
```bash
# Backend
docker run -p 5000:5000 marketdialogue/vcareer-ops-api:3.5.0

# Frontend (separate terminal)
docker run -p 5173:5173 marketdialogue/vcareer-ops-dashboard:3.5.0
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    image: marketdialogue/vcareer-ops-api:3.5.0
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped

  dashboard:
    image: marketdialogue/vcareer-ops-dashboard:3.5.0
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE=http://api:5000
    depends_on:
      - api
    restart: unless-stopped
```

---

## 📈 Version Management

### Push Version 3.5.0
```bash
docker-build-marketdialogue.bat 3.5.0
docker-push-marketdialogue.bat 3.5.0
```

Creates tags:
- `3.5.0`
- `latest` (points to 3.5.0)

### Later Push Version 3.6.0
```bash
docker-build-marketdialogue.bat 3.6.0
docker-push-marketdialogue.bat 3.6.0
```

Creates tags:
- `3.6.0`
- `latest` (now points to 3.6.0)

Both versions stay available!

---

## ✅ Verification

### Check Images Built
```bash
docker images | findstr marketdialogue
```

Should show:
```
marketdialogue/vcareer-ops-api        3.5.0     63.3MB
marketdialogue/vcareer-ops-api        latest    63.3MB
marketdialogue/vcareer-ops-dashboard  3.5.0     50MB
marketdialogue/vcareer-ops-dashboard  latest    50MB
```

### Check on Docker Hub
Visit: https://hub.docker.com/u/marketdialogue

Should list:
- vcareer-ops-api (with tags: 3.5.0, latest)
- vcareer-ops-dashboard (with tags: 3.5.0, latest)

---

## 🆘 Troubleshooting

### "Not logged in"
```bash
docker login
# Enter credentials for marketdialogue account
```

### "Image not found"
```bash
# Make sure you built first
docker-build-marketdialogue.bat 3.5.0

# Then push
docker-push-marketdialogue.bat 3.5.0
```

### "Authorization failed"
```bash
# Re-login
docker logout
docker login
# Enter correct credentials
```

### "Network timeout"
```bash
# Check internet connection
# Try pushing again
docker-push-marketdialogue.bat 3.5.0
```

---

## 📚 Files Included

| File | Purpose |
|------|---------|
| `docker-build-marketdialogue.bat` | Build for your namespace |
| `docker-push-marketdialogue.bat` | Push to your namespace |
| `Dockerfile` | Backend image definition |
| `dashboard-web/Dockerfile.prod` | Frontend image definition |

---

## 🎯 Quick Commands

```bash
# Build
docker-build-marketdialogue.bat 3.5.0

# Login
docker login

# Push
docker-push-marketdialogue.bat 3.5.0

# Verify
docker images | findstr marketdialogue

# Pull anywhere
docker pull marketdialogue/vcareer-ops-api:3.5.0
```

---

**Status: ✅ Ready for marketdialogue Docker Hub**

Run the build and push scripts above to deploy! 🚀

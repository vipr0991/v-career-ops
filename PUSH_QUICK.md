# 🚀 Quick Push Guide - marketdialogue/vcareer-ops

## 3 Commands to Deploy

### 1️⃣ Build
```bash
cd career-ops
docker-build-marketdialogue.bat 3.5.0
```

### 2️⃣ Login
```bash
docker login
# Username: marketdialogue
# Password: [your Docker Hub password]
```

### 3️⃣ Push
```bash
docker-push-marketdialogue.bat 3.5.0
```

---

## Done! ✅

Your images are now on Docker Hub:

**Pull anywhere:**
```bash
docker pull marketdialogue/vcareer-ops-api:3.5.0
docker pull marketdialogue/vcareer-ops-dashboard:3.5.0
```

**View on Docker Hub:**
- https://hub.docker.com/r/marketdialogue/vcareer-ops-api
- https://hub.docker.com/r/marketdialogue/vcareer-ops-dashboard

---

## What Gets Created

```
marketdialogue/vcareer-ops-api:3.5.0
marketdialogue/vcareer-ops-api:latest

marketdialogue/vcareer-ops-dashboard:3.5.0
marketdialogue/vcareer-ops-dashboard:latest
```

---

## Image Info

**Backend API**
- Size: 63.3 MB
- Port: 5000
- Base: Python 3.11-slim

**Frontend Dashboard**
- Size: ~50 MB
- Port: 5173
- Base: Node 20-alpine

---

**Everything is ready! Run the 3 commands above. 🎉**

# ✅ UNIFIED REPOSITORY - PUSH COMPLETE

## Single Repository with Multiple Tags

Both Career-Ops images are now in **one repository** with different tags:

**Repository:** `marketdialogue/vcareer-ops`

---

## All Tags Available

```
marketdialogue/vcareer-ops:api-3.5.0         ← Backend API v3.5.0 (63.3 MB)
marketdialogue/vcareer-ops:api-latest        ← Backend API latest
marketdialogue/vcareer-ops:dashboard-3.5.0   ← Frontend Dashboard v3.5.0 (52.4 MB)
marketdialogue/vcareer-ops:dashboard-latest  ← Frontend Dashboard latest
```

---

## How to Pull

### Backend API
```bash
docker pull marketdialogue/vcareer-ops:api-3.5.0
docker pull marketdialogue/vcareer-ops:api-latest
```

### Frontend Dashboard
```bash
docker pull marketdialogue/vcareer-ops:dashboard-3.5.0
docker pull marketdialogue/vcareer-ops:dashboard-latest
```

---

## How to Run

### Backend
```bash
docker run -p 5000:5000 marketdialogue/vcareer-ops:api-latest
```

### Frontend
```bash
docker run -p 5173:5173 marketdialogue/vcareer-ops:dashboard-latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    image: marketdialogue/vcareer-ops:api-latest
    ports:
      - "5000:5000"
    
  dashboard:
    image: marketdialogue/vcareer-ops:dashboard-latest
    ports:
      - "5173:5173"
    depends_on:
      - api
```

---

## View on Docker Hub

Single repository with all tags:
https://hub.docker.com/r/marketdialogue/vcareer-ops

---

## What's Included

✅ Backend API (Python FastAPI) - 63.3 MB  
✅ Frontend Dashboard (React) - 52.4 MB  
✅ Both versioned (3.5.0) and latest tags  
✅ Production-ready multi-stage builds  
✅ Health checks built-in  
✅ All in one repository  

---

**Status: ✅ COMPLETE**

Both images are live on Docker Hub in a single, unified repository! 🚀

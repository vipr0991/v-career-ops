#!/bin/bash
# Build script for Docker Hub deployment
# Usage: ./docker-build.sh [REGISTRY] [VERSION]
# Example: ./docker-build.sh myregistry careerops 3.5.0

set -e

REGISTRY="${1:-docker.io}"
NAMESPACE="${2:-yourusername}"
VERSION="${3:-3.5.0}"

BACKEND_IMAGE="${REGISTRY}/${NAMESPACE}/career-ops-api:${VERSION}"
FRONTEND_IMAGE="${REGISTRY}/${NAMESPACE}/career-ops-dashboard:${VERSION}"
LATEST_BACKEND="${REGISTRY}/${NAMESPACE}/career-ops-api:latest"
LATEST_FRONTEND="${REGISTRY}/${NAMESPACE}/career-ops-dashboard:latest"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CAREER-OPS DOCKER BUILD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Registry:  $REGISTRY"
echo "Namespace: $NAMESPACE"
echo "Version:   $VERSION"
echo ""

# Build Backend
echo "[1/2] Building Backend API..."
echo "      Image: $BACKEND_IMAGE"
docker build \
  --file Dockerfile \
  --tag "$BACKEND_IMAGE" \
  --tag "$LATEST_BACKEND" \
  --build-arg VERSION="$VERSION" \
  --label "version=$VERSION" \
  --label "maintainer=careerops" \
  .

echo "      ✓ Backend built"
echo ""

# Build Frontend
echo "[2/2] Building Frontend Dashboard..."
echo "      Image: $FRONTEND_IMAGE"
docker build \
  --file dashboard-web/Dockerfile.prod \
  --tag "$FRONTEND_IMAGE" \
  --tag "$LATEST_FRONTEND" \
  --build-arg VERSION="$VERSION" \
  --label "version=$VERSION" \
  --label "maintainer=careerops" \
  dashboard-web/

echo "      ✓ Frontend built"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  BUILD COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Images built:"
echo "  Backend:  $BACKEND_IMAGE"
echo "  Frontend: $FRONTEND_IMAGE"
echo ""
echo "Next steps:"
echo "  1. docker login"
echo "  2. docker push $BACKEND_IMAGE"
echo "  3. docker push $FRONTEND_IMAGE"
echo "  4. docker push $LATEST_BACKEND"
echo "  5. docker push $LATEST_FRONTEND"
echo ""

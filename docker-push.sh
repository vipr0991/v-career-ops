#!/bin/bash
# Push images to Docker Hub
# Usage: ./docker-push.sh [REGISTRY] [NAMESPACE] [VERSION]

set -e

REGISTRY="${1:-docker.io}"
NAMESPACE="${2:-yourusername}"
VERSION="${3:-3.5.0}"

BACKEND_IMAGE="${REGISTRY}/${NAMESPACE}/career-ops-api:${VERSION}"
FRONTEND_IMAGE="${REGISTRY}/${NAMESPACE}/career-ops-dashboard:${VERSION}"
LATEST_BACKEND="${REGISTRY}/${NAMESPACE}/career-ops-api:latest"
LATEST_FRONTEND="${REGISTRY}/${NAMESPACE}/career-ops-dashboard:latest"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CAREER-OPS DOCKER PUSH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Registry:  $REGISTRY"
echo "Namespace: $NAMESPACE"
echo "Version:   $VERSION"
echo ""
echo "Login to Docker Hub first:"
echo "  docker login"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

echo ""
echo "[1/4] Pushing Backend versioned image..."
docker push "$BACKEND_IMAGE"

echo ""
echo "[2/4] Pushing Backend latest image..."
docker push "$LATEST_BACKEND"

echo ""
echo "[3/4] Pushing Frontend versioned image..."
docker push "$FRONTEND_IMAGE"

echo ""
echo "[4/4] Pushing Frontend latest image..."
docker push "$LATEST_FRONTEND"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PUSH COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Images available:"
echo "  Backend:  $REGISTRY/$NAMESPACE/career-ops-api"
echo "  Frontend: $REGISTRY/$NAMESPACE/career-ops-dashboard"
echo ""
echo "Usage:"
echo "  docker run -p 5000:5000 $BACKEND_IMAGE"
echo "  docker run -p 5173:5173 $FRONTEND_IMAGE"
echo ""

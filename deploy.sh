#!/bin/bash
# ============================================================
# Swiftor Deployment Script for Hostinger VPS
# ============================================================

set -e

echo "==================================="
echo "  Swiftor Deployment Script"
echo "==================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Copy .env.production to .env and fill in the values:"
    echo "  cp .env.production .env"
    echo "  nano .env"
    exit 1
fi

# Check required variables
source .env
if [ -z "$SECRET_KEY" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: Required environment variables not set!"
    echo "Please fill in SECRET_KEY, POSTGRES_PASSWORD, and OPENAI_API_KEY in .env"
    exit 1
fi

# Create SSL directory if it doesn't exist
mkdir -p ssl

echo ""
echo "Step 1: Pulling latest code..."
git pull origin master || echo "Not a git repo or no remote, skipping pull"

echo ""
echo "Step 2: Building Docker images..."
docker compose build --no-cache

echo ""
echo "Step 3: Stopping existing containers..."
docker compose down || true

echo ""
echo "Step 4: Starting containers..."
docker compose up -d

echo ""
echo "Step 5: Waiting for services to be healthy..."
sleep 10

echo ""
echo "Step 6: Checking container status..."
docker compose ps

echo ""
echo "==================================="
echo "  Deployment Complete!"
echo "==================================="
echo ""
echo "Your app should be running at:"
echo "  - HTTP:  http://your-server-ip"
echo "  - API:   http://your-server-ip/api"
echo "  - Docs:  http://your-server-ip/docs"
echo ""
echo "To view logs:"
echo "  docker compose logs -f"
echo ""
echo "To check health:"
echo "  curl http://localhost/health"
echo "  curl http://localhost:8000/health"
echo ""

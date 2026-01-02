#!/bin/bash
# Production Deployment Script for Hostinger/VPS

set -e  # Exit on error

echo "=========================================="
echo "Travel News Translator - Production Deploy"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create .env from .env.production template"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}Error: OPENAI_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_TO_A_RANDOM_32_CHAR_STRING" ]; then
    echo -e "${RED}Error: SECRET_KEY not set or using default value${NC}"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi

echo -e "${GREEN}✓${NC} Environment variables loaded"
echo ""

# Pull latest code (if using git)
# echo "Pulling latest code..."
# git pull origin main

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build images
echo "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
echo "Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database
echo "Waiting for database..."
sleep 5

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Create initial admin user (optional)
# echo "Creating admin user..."
# docker-compose -f docker-compose.prod.yml exec backend python -c "
# from app.database import SessionLocal
# from app.models.user import User
# from passlib.context import CryptContext
# db = SessionLocal()
# pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# if not db.query(User).filter(User.email == 'admin@example.com').first():
#     admin = User(
#         email='admin@example.com',
#         hashed_password=pwd_context.hash('admin123'),
#         full_name='Admin User',
#         is_admin=True,
#         is_active=True,
#         monthly_token_limit=1000000
#     )
#     db.add(admin)
#     db.commit()
#     print('Admin user created')
# "

# Show status
echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Services Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "Access your app:"
echo "  - Frontend: http://YOUR_SERVER_IP"
echo "  - API Docs: http://YOUR_SERVER_IP/api/docs"
echo ""
echo "View logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "Stop services:"
echo "  docker-compose -f docker-compose.prod.yml down"
echo ""

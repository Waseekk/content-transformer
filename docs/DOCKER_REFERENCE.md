# Docker Commands Reference

Quick reference for Docker operations with Swiftor.

## Table of Contents

1. [Basic Commands](#basic-commands)
2. [Service Management](#service-management)
3. [Logs & Debugging](#logs--debugging)
4. [Database Operations](#database-operations)
5. [SSL Certificate Management](#ssl-certificate-management)
6. [Maintenance](#maintenance)

---

## Basic Commands

### Build Images
```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend

# Build with no cache (clean build)
docker compose build --no-cache
```

### Start Services
```bash
# Start all services (detached)
docker compose up -d

# Start specific service
docker compose up -d backend

# Start with logs visible
docker compose up

# Rebuild and start
docker compose up -d --build
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes data!)
docker compose down -v

# Stop specific service
docker compose stop backend
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

---

## Service Management

### Check Status
```bash
# List running containers
docker compose ps

# Show resource usage
docker stats

# Show container details
docker compose inspect backend
```

### Scale Services
```bash
# Run multiple backend instances (requires load balancer)
docker compose up -d --scale backend=3
```

### Execute Commands in Container
```bash
# Open shell in backend
docker compose exec backend bash

# Run Python command
docker compose exec backend python -c "print('Hello')"

# Run Django/FastAPI management commands
docker compose exec backend python -m app.manage migrate
```

---

## Logs & Debugging

### View Logs
```bash
# All services
docker compose logs

# Follow logs (live)
docker compose logs -f

# Specific service
docker compose logs backend
docker compose logs -f backend

# Last N lines
docker compose logs --tail=100 backend

# Since timestamp
docker compose logs --since="2024-01-01" backend
```

### Debug Container
```bash
# Check container health
docker compose exec backend curl http://localhost:8000/health

# View environment variables
docker compose exec backend env

# Check network connectivity
docker compose exec backend ping postgres

# View running processes
docker compose exec backend ps aux
```

---

## Database Operations

### Backup PostgreSQL
```bash
# Full database backup
docker compose exec postgres pg_dump -U swiftor swiftor > backup_$(date +%Y%m%d).sql

# Compressed backup
docker compose exec postgres pg_dump -U swiftor swiftor | gzip > backup_$(date +%Y%m%d).sql.gz

# Specific tables only
docker compose exec postgres pg_dump -U swiftor -t users -t articles swiftor > users_articles.sql
```

### Restore PostgreSQL
```bash
# From SQL file
cat backup.sql | docker compose exec -T postgres psql -U swiftor -d swiftor

# From compressed file
gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U swiftor -d swiftor
```

### Database Shell
```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U swiftor -d swiftor

# Common psql commands:
# \dt          - List tables
# \d tablename - Describe table
# \q           - Quit
```

### Database Queries
```bash
# Row counts
docker compose exec postgres psql -U swiftor -d swiftor -c "SELECT COUNT(*) FROM users;"

# Recent data
docker compose exec postgres psql -U swiftor -d swiftor -c "SELECT * FROM articles ORDER BY created_at DESC LIMIT 5;"
```

---

## SSL Certificate Management

### Initial Setup
```bash
# Stop frontend to free port 80
docker compose stop frontend

# Get certificate
certbot certonly --standalone -d your-domain.com

# Copy certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# Restart frontend
docker compose up -d frontend
```

### Manual Renewal
```bash
# Stop frontend
docker compose stop frontend

# Renew certificate
certbot renew

# Copy new certificates
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/

# Restart frontend
docker compose up -d frontend
```

### Auto-Renewal (Cron)
```bash
# Add to crontab
crontab -e

# Add this line (runs at 3 AM daily):
0 3 * * * certbot renew --quiet && docker compose -f /home/swiftor/swiftor/docker-compose.yml restart frontend
```

### Check Certificate Status
```bash
# Check expiry
certbot certificates

# Check from outside
openssl s_client -connect your-domain.com:443 -servername your-domain.com 2>/dev/null | openssl x509 -noout -dates
```

---

## Maintenance

### Clean Up Docker
```bash
# Remove unused images
docker image prune

# Remove all unused resources (CAUTION)
docker system prune

# Remove everything including volumes (DANGER!)
docker system prune -a --volumes
```

### Update Deployment
```bash
# Pull latest code
git pull

# Rebuild affected services
docker compose build backend frontend

# Restart with new images
docker compose up -d

# Watch logs for errors
docker compose logs -f
```

### Check Disk Usage
```bash
# Docker disk usage
docker system df

# Volume sizes
docker volume ls
docker volume inspect postgres_data
```

### Health Checks
```bash
# Application health
curl http://localhost/health

# Check all service statuses
docker compose ps

# Check container health status
docker inspect --format='{{.State.Health.Status}}' swiftor-backend-1
```

---

## Common Issues & Fixes

### Container Won't Start
```bash
# Check logs
docker compose logs backend

# Check for port conflicts
lsof -i :8000

# Restart Docker daemon
systemctl restart docker
```

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec backend python -c "from app.core.database import engine; engine.connect(); print('OK')"

# Check environment variables
docker compose exec backend env | grep DATABASE
```

### Out of Memory
```bash
# Check memory usage
docker stats

# Increase swap (if needed)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Playwright Issues
```bash
# Check Chromium installation
docker compose exec backend playwright install --dry-run

# Reinstall Chromium
docker compose exec backend playwright install chromium

# Check for missing dependencies
docker compose exec backend playwright install-deps
```

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Start all | `docker compose up -d` |
| Stop all | `docker compose down` |
| View logs | `docker compose logs -f` |
| Restart | `docker compose restart` |
| Rebuild | `docker compose build --no-cache` |
| DB backup | `docker compose exec postgres pg_dump -U swiftor swiftor > backup.sql` |
| DB restore | `cat backup.sql \| docker compose exec -T postgres psql -U swiftor -d swiftor` |
| Shell | `docker compose exec backend bash` |
| Status | `docker compose ps` |
| Clean | `docker system prune` |

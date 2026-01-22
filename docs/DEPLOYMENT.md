# Swiftor Deployment Guide

Complete guide for deploying Swiftor to Hostinger VPS using Docker.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Setup](#vps-setup)
3. [Project Upload](#project-upload)
4. [Environment Configuration](#environment-configuration)
5. [Build & Deploy](#build--deploy)
6. [SSL Setup](#ssl-setup)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)
9. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Software
- Docker Engine 24.0+
- Docker Compose v2+
- Git

### Required Credentials
- OpenAI API Key (`OPENAI_API_KEY`)
- Domain name pointed to VPS IP
- SSH access to VPS

### Optional Credentials
- Google OAuth Client ID/Secret (for Google login)

### Minimum VPS Requirements
- 2 vCPU
- 4GB RAM
- 20GB SSD
- Ubuntu 22.04 LTS or Debian 12

---

## VPS Setup

### Step 1: Connect to VPS
```bash
ssh root@your-vps-ip
```

### Step 2: Update System
```bash
apt update && apt upgrade -y
```

### Step 3: Install Docker
```bash
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin -y
```

### Step 4: Verify Installation
```bash
docker --version
docker compose version
```

### Step 5: Create Non-Root User (Recommended)
```bash
adduser swiftor
usermod -aG docker swiftor
su - swiftor
```

---

## Project Upload

### Option A: Git Clone (Recommended)
```bash
cd /home/swiftor
git clone <your-repo-url> swiftor
cd swiftor
```

### Option B: Manual Upload
```bash
# From local machine
scp -r ./project/* swiftor@your-vps-ip:/home/swiftor/swiftor/
```

---

## Environment Configuration

### Step 1: Create .env File
```bash
cd /home/swiftor/swiftor
cp .env.production .env
```

### Step 2: Generate Secret Key
```bash
openssl rand -hex 32
# Copy output to SECRET_KEY in .env
```

### Step 3: Edit Environment Variables
```bash
nano .env
```

**Required Variables:**
```env
# Security
SECRET_KEY=<your-generated-secret-key>

# Database
POSTGRES_USER=swiftor
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=swiftor

# API Keys
OPENAI_API_KEY=sk-...

# URLs
FRONTEND_URL=https://your-domain.com

# Optional: OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Step 4: Verify Permissions
```bash
chmod 600 .env
```

---

## Build & Deploy

### Step 1: Build Images
```bash
docker compose build
```

This will:
- Build React frontend with Vite
- Install Python dependencies
- Install Playwright and Chromium
- Create optimized production images

**Expected build time:** 5-10 minutes

### Step 2: Start Services
```bash
docker compose up -d
```

### Step 3: View Logs
```bash
docker compose logs -f
```

### Step 4: Check Service Status
```bash
docker compose ps
```

All services should show `running` status.

---

## SSL Setup

### Step 1: Install Certbot
```bash
apt install certbot -y
```

### Step 2: Stop Frontend (Temporarily)
```bash
docker compose stop frontend
```

### Step 3: Get Certificate
```bash
certbot certonly --standalone -d your-domain.com
```

### Step 4: Copy Certificates
```bash
mkdir -p ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
```

### Step 5: Enable SSL in Nginx
Edit `docker/nginx.conf`:
- Uncomment the SSL server block (port 443)
- Update certificate paths

### Step 6: Restart Frontend
```bash
docker compose up -d frontend
```

### Step 7: Auto-Renewal Setup
```bash
echo "0 3 * * * certbot renew --quiet && docker compose restart frontend" | crontab -
```

---

## Verification

Run these checks after deployment:

### Health Check
```bash
curl http://localhost/health
# Expected: {"status":"healthy","database":"connected"}
```

### Frontend Load
```bash
curl -I http://localhost/
# Expected: HTTP/1.1 200 OK
```

### API Documentation
```bash
curl http://localhost/api/docs
# Expected: OpenAPI docs HTML
```

### Database Connection
```bash
docker compose exec backend python -c "from app.core.database import engine; print('DB OK')"
```

### Full Checklist
- [ ] All services show `running` in `docker compose ps`
- [ ] Health endpoint returns healthy
- [ ] Frontend loads in browser
- [ ] Login/Register works
- [ ] Translation API works
- [ ] Scraper runs successfully
- [ ] SSL certificate valid (green padlock)

---

## Troubleshooting

### Container Won't Start
```bash
docker compose logs <service-name>
docker compose down
docker compose up -d
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Verify environment
docker compose exec backend env | grep POSTGRES
```

### Playwright/Chromium Issues
```bash
# Check Chromium is installed
docker compose exec backend playwright install --dry-run

# Reinstall if needed
docker compose exec backend playwright install chromium
```

### Port Already in Use
```bash
# Find process using port 80
lsof -i :80

# Kill process or change port in docker-compose.yml
```

### Out of Disk Space
```bash
# Clean unused Docker images
docker system prune -a

# Check disk usage
df -h
```

### Permission Denied Errors
```bash
# Fix volume permissions
chown -R 1000:1000 ./data ./logs
```

---

## Rollback Procedures

### Rollback to Previous Version
```bash
# Stop current services
docker compose down

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild and restart
docker compose build
docker compose up -d
```

### Restore Database Backup
```bash
# Stop services
docker compose down

# Restore backup
cat backup.sql | docker compose exec -T postgres psql -U swiftor -d swiftor

# Restart services
docker compose up -d
```

### Complete Rollback
```bash
# Stop and remove everything
docker compose down -v

# Remove project
rm -rf /home/swiftor/swiftor

# Start fresh
git clone <repo> /home/swiftor/swiftor
cd /home/swiftor/swiftor
cp .env.production .env
docker compose build
docker compose up -d
```

---

## Maintenance

### Daily Tasks
- Check service health: `docker compose ps`
- Monitor logs: `docker compose logs --tail=100`

### Weekly Tasks
- Database backup: See [DOCKER_REFERENCE.md](./DOCKER_REFERENCE.md)
- Check disk space: `df -h`
- Update dependencies (test in staging first)

### Monthly Tasks
- SSL certificate check (should auto-renew)
- Security updates: `apt update && apt upgrade`
- Review logs for errors

---

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Review this guide's troubleshooting section
3. Check GitHub Issues: <repo-url>/issues

# Swiftor Deployment Log

**Date:** 2026-01-29
**VPS Provider:** Hostinger
**Server:** srv1217751.hstgr.cloud
**IP Address:** 46.202.160.112
**Domain:** swiftor.online

---

## Table of Contents

1. [Pre-Deployment Audit](#pre-deployment-audit)
2. [Issues Found & Fixed](#issues-found--fixed)
3. [VPS Configuration](#vps-configuration)
4. [Docker Deployment](#docker-deployment)
5. [Firewall Configuration](#firewall-configuration)
6. [Domain & SSL Setup](#domain--ssl-setup)
7. [Final Verification](#final-verification)
8. [Access Information](#access-information)
9. [Troubleshooting Notes](#troubleshooting-notes)

---

## Pre-Deployment Audit

### Audit Summary

| Area | Status | Notes |
|------|--------|-------|
| Docker Config | ✅ Ready | Full stack with Caddy |
| Caddyfile Proxy | ✅ Ready | All API routes covered |
| Frontend Config | ✅ Fixed | Removed hardcoded IP |
| Git Security | ✅ Secure | No secrets exposed |
| .gitignore | ✅ Updated | Added *.stackdump |

### Files Audited
- `docker-compose.yml` - Full stack configuration
- `Dockerfile.backend` - Multi-stage build with Playwright
- `Dockerfile.frontend` - Multi-stage build with Caddy
- `docker/Caddyfile` - Reverse proxy configuration
- `frontend/.env` - Development environment
- `frontend/.env.production` - Production environment
- `.gitignore` - Git ignore patterns

---

## Issues Found & Fixed

### 1. Hardcoded IP in frontend/.env (CRITICAL)

**File:** `frontend/.env`
**Issue:** `VITE_WS_URL=http://46.202.160.112:8000`
**Fix:** Changed to `VITE_WS_URL=` (empty)
**Note:** This file is gitignored (local dev only)

### 2. Missing .gitignore Entry (LOW)

**File:** `.gitignore`
**Issue:** `bash.exe.stackdump` untracked
**Fix:** Added `*.stackdump` pattern
**Commit:** `b192ded`

### 3. Git Branch Mismatch (CRITICAL)

**Issue:** VPS was on `master` branch, development on `swiftor` branch
**Fix:** Merged `swiftor` into `master`
**Commit:** `d92be8d` - "Merge swiftor branch: frontend deployment with Caddy, Docker fixes, audit cleanup"

### 4. Missing Frontend Container (CRITICAL)

**Issue:** VPS docker-compose.yml only had backend, postgres, redis (no frontend)
**Fix:** Merged swiftor branch which includes full frontend configuration

---

## VPS Configuration

### System Specifications

| Resource | Value |
|----------|-------|
| OS | Ubuntu (Linux) |
| RAM | 3915 MB total, ~2700 MB available |
| Disk | 48 GB total, 21 GB available (57% used) |
| Swap | None configured |

### Directory Structure

```
/root/projects/swiftor/     # Swiftor application
/docker/n8n/                 # n8n workflow automation (separate)
```

### Environment Variables (.env)

```env
# Database
POSTGRES_USER=swiftor
POSTGRES_PASSWORD=<secure-password>
POSTGRES_DB=swiftor
DATABASE_URL=postgresql://swiftor:<password>@postgres:5432/swiftor

# Security
SECRET_KEY=<random-string>

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Frontend URL
FRONTEND_URL=https://swiftor.online

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### User Configuration

| Email | Role | Status |
|-------|------|--------|
| waseekirtefa@gmail.com | Admin | Active |

**Admin Promotion Command:**
```bash
docker exec swiftor-postgres psql -U swiftor -d swiftor -c "UPDATE users SET is_admin = true WHERE email = 'waseekirtefa@gmail.com';"
```

---

## Docker Deployment

### Running Containers

| Container | Image | Port | Status |
|-----------|-------|------|--------|
| swiftor-frontend | swiftor-frontend | 8080:80 | Healthy |
| swiftor-backend | swiftor-backend | 8000 (internal) | Healthy |
| swiftor-postgres | postgres:16-alpine | 5432 (internal) | Healthy |
| swiftor-redis | redis:7-alpine | 6379 (internal) | Healthy |

### Docker Networks

| Network | Purpose |
|---------|---------|
| swiftor_swiftor-network | Internal communication |
| n8n_default | Traefik integration for HTTPS |

### Deployment Commands

```bash
# Pull latest code
cd /root/projects/swiftor
git pull origin master

# Update environment
sed -i 's|FRONTEND_URL=.*|FRONTEND_URL=https://swiftor.online|' .env

# Deploy
docker compose down
docker compose build --no-cache
docker compose up -d

# Verify
docker compose ps
```

### Build Notes

- Backend build: ~5 minutes (includes Playwright/Chromium)
- Frontend build: ~4 minutes (npm install + Vite build)
- Total deployment time: ~10 minutes

---

## Firewall Configuration

### Hostinger Firewall Rules

| Action | Protocol | Port | Source | Description |
|--------|----------|------|--------|-------------|
| Accept | SSH | 22 | Any | SSH access |
| Accept | HTTP | 80 | Any | Traefik (n8n) |
| Accept | HTTPS | 443 | Any | Traefik (n8n + Swiftor) |
| Accept | TCP | 8000 | Any | Backend API (optional) |
| Accept | TCP | 8080 | Any | Swiftor direct access |
| Drop | Any | Any | Any | Default deny |

**Important:** After adding rules, click **"Synchronize"** to apply changes.

### UFW Status

```
Status: inactive
```
(Using Hostinger's external firewall instead)

---

## Domain & SSL Setup

### DNS Configuration (swiftor.online)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 46.202.160.112 | 14400 |
| CAA | @ | 0 issue "letsencrypt.org" | 14400 |

**Note:** www subdomain not configured (optional)

### Traefik Configuration

Swiftor uses the existing Traefik instance from n8n for HTTPS.

**docker-compose.yml labels:**
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.swiftor.rule=Host(`swiftor.online`)"
  - "traefik.http.routers.swiftor.tls=true"
  - "traefik.http.routers.swiftor.entrypoints=web,websecure"
  - "traefik.http.routers.swiftor.tls.certresolver=mytlschallenge"
  - "traefik.http.services.swiftor.loadbalancer.server.port=80"
```

### SSL Certificate

- **Provider:** Let's Encrypt (via Traefik ACME)
- **Type:** TLS Challenge
- **Auto-renewal:** Yes (managed by Traefik)

### Traefik Restart (if SSL issues)

```bash
cd /docker/n8n
docker compose restart traefik
```

---

## Final Verification

### Playwright Automated Test Results

| Test | Result |
|------|--------|
| Navigate to https://swiftor.online | ✅ Redirects to /login |
| SSL Certificate | ✅ Valid (Let's Encrypt) |
| Login with credentials | ✅ Success |
| Dashboard loads | ✅ All components visible |
| Navigation menu | ✅ All links working |
| News Sources | ✅ 13 of 13 enabled |
| API connection | ✅ Connected |

### Manual Verification Commands

```bash
# Check containers
docker compose ps

# Check backend health
docker exec swiftor-backend curl -s http://localhost:8000/health

# Check database
docker exec swiftor-postgres psql -U swiftor -d swiftor -c "SELECT id, email, is_admin FROM users;"

# Check Traefik logs
docker logs n8n-traefik-1 --tail 20

# Test frontend locally
curl -s http://localhost:8080/ | head -5

# Test SSL certificate
echo | openssl s_client -connect swiftor.online:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Access Information

### URLs

| URL | Purpose | Auth Required |
|-----|---------|---------------|
| https://swiftor.online | Production (HTTPS) | Yes |
| http://46.202.160.112:8080 | Fallback (HTTP) | Yes |
| http://46.202.160.112:8000 | Backend API direct | No |

### Admin Credentials

| Field | Value |
|-------|-------|
| Email | waseekirtefa@gmail.com |
| Password | SWIFTOR1234a |
| Role | Admin |

### VPS Access

| Field | Value |
|-------|-------|
| IP | 46.202.160.112 |
| User | root |
| SSH | `ssh root@46.202.160.112` |

---

## Troubleshooting Notes

### Issue: "This site can't be reached" (ERR_CONNECTION_TIMED_OUT)

**Cause:** Hostinger firewall blocking port
**Fix:** Add firewall rule in Hostinger panel → Synchronize

### Issue: SSL Certificate Error (www.swiftor.online)

**Cause:** www DNS record not configured
**Fix:** Either add www A record OR remove www from Traefik config
**Applied Fix:** Removed www from docker-compose.yml labels

### Issue: "Incorrect email or password"

**Cause:** Wrong password
**Fix:** Reset password via:
```bash
docker exec swiftor-backend python -c "
from app.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext
pwd = CryptContext(schemes=['bcrypt'])
db = SessionLocal()
user = db.query(User).filter(User.email == 'waseekirtefa@gmail.com').first()
user.hashed_password = pwd.hash('NEW_PASSWORD_HERE')
db.commit()
print('Password reset!')
"
```

### Issue: API returns 404 for /api/health

**Cause:** Backend health endpoint is at `/health`, not `/api/health`
**Note:** This is expected behavior - health checks work internally

### Issue: Old SSL error in Traefik logs

**Cause:** Cached error from previous failed attempt
**Fix:** Restart Traefik: `cd /docker/n8n && docker compose restart traefik`
**Note:** If HTTPS works in browser, ignore old log entries

### Issue: Gateway Timeout (502/504) after running for extended period

**Cause:** Traefik's internal routing state and SSL certificate cache becomes stale after running for 24+ hours without any configuration changes. This can cause intermittent gateway timeouts even when all containers are healthy.

**Symptoms:**
- https://swiftor.online shows "Gateway Timeout"
- `docker compose ps` shows all containers as "healthy"
- `curl -I http://localhost:8080` works (direct access succeeds)
- Traefik logs show no new errors

**Diagnosis:**
```bash
# Check containers are healthy
docker compose ps

# Test direct access (bypass Traefik)
curl -I http://localhost:8080

# Check frontend is on Traefik's network
docker network inspect n8n_default | grep -A2 swiftor

# Check Traefik sees the router
docker exec n8n-traefik-1 wget -qO- http://localhost:8080/api/http/routers 2>/dev/null | grep -i swiftor
```

**Fix:** Restart Traefik to refresh its internal state:
```bash
cd /docker/n8n && docker compose restart traefik
```

**Prevention:** Consider setting up a periodic Traefik restart via cron (e.g., weekly) or monitoring for gateway timeouts.

---

## Coexisting Services

### n8n Workflow Automation

| Service | Port | Domain |
|---------|------|--------|
| Traefik | 80, 443 | - |
| n8n | 5678 (localhost) | n8n.srv1217751.hstgr.cloud |

**Location:** `/docker/n8n/`

**Note:** Swiftor uses n8n's Traefik instance for HTTPS. Both services coexist without conflict.

---

## Commits Made During Deployment

| Commit | Message |
|--------|---------|
| `b192ded` | chore: add stackdump files to gitignore |
| `d92be8d` | Merge swiftor branch: frontend deployment with Caddy, Docker fixes, audit cleanup |
| `e2101eb` | feat: add Traefik labels for swiftor.online domain support |
| `4b52b49` | fix: remove www subdomain from Traefik config |

---

## Future Improvements

- [ ] Add www.swiftor.online DNS record for www support
- [ ] Configure automated database backups
- [ ] Set up monitoring/alerting
- [ ] Add rate limiting to API
- [ ] Configure log rotation

---

*Last updated: 2026-01-30*

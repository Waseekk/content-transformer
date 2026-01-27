# Swiftor Deployment Troubleshooting Guide

## Deployment Overview

- **VPS**: 46.202.160.112 (Ubuntu 24.04)
- **Domain**: swiftor.online
- **Repository**: https://github.com/Waseekk/content-transformer
- **Deploy Path**: `/root/projects/swiftor`

---

## Issue 1: `npm ci` Failed in Docker Build

### Error
```
[frontend frontend-builder 4/6] RUN npm ci --silent
target frontend: failed to solve: process "/bin/sh -c npm ci --silent" did not complete successfully: exit code: 1
```

### Cause
`npm ci` requires a `package-lock.json` file to exist. The `package-lock.json` was in `.gitignore`, so it wasn't pushed to the repository.

### Solution
Changed `Dockerfile` line 21 from:
```dockerfile
RUN npm ci --silent
```
To:
```dockerfile
RUN npm install --silent
```

### File Changed
`Dockerfile` (in project root)

---

## Issue 2: TypeScript Build Errors

### Error
```
src/components/common/Layout.tsx(11,1): error TS6133: 'SwiftorLogo' is declared but its value is never read.
src/components/common/Layout.tsx(110,66): error TS2322: Type '"steps(2)"' is not assignable to type 'Easing | Easing[] | undefined'.
src/pages/ArticlesPage.tsx(21,3): error TS6133: 'HiRefresh' is declared but its value is never read.
src/pages/SupportPage.tsx(22,3): error TS6133: 'HiChevronUp' is declared but its value is never read.
```

### Cause
1. Unused imports that TypeScript strict mode flags as errors
2. Invalid framer-motion easing value `'steps(2)'` - not a valid Easing type

### Solution

**Layout.tsx:**
```diff
- import { SwiftorLogo } from './SwiftorLogo';
```
```diff
- transition={{ duration: 0.8, repeat: Infinity, ease: 'steps(2)' }}
+ transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
```

**ArticlesPage.tsx:**
```diff
  import {
    HiFilter,
    HiClock,
-   HiRefresh,
    HiSearch,
```

**SupportPage.tsx:**
```diff
    HiChevronDown,
-   HiChevronUp,
    HiRefresh,
```

### Commit
```
fix: TypeScript errors and production API URL handling
Commit: 4f21074
```

---

## Issue 3: API URL Configuration for Production

### Problem
Frontend was hardcoded to use `http://localhost:8000` which doesn't work in production.

### Cause
Using `||` (logical OR) with environment variables:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```
When `VITE_API_URL` is set to empty string `''`, the `||` operator still falls back to localhost because empty string is falsy.

### Solution
Changed to nullish coalescing `??` and appropriate defaults:

**frontend/src/api/axios.ts:**
```javascript
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
```

**frontend/src/services/axios.ts:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';
```

**frontend/src/services/websocket.ts:**
```javascript
const WS_URL = import.meta.env.VITE_API_URL?.replace('/api', '') ?? '';
```

**frontend/src/pages/ArticlesPage.tsx:**
```javascript
const response = await fetch(
  `${import.meta.env.VITE_API_BASE_URL ?? ''}/api/articles?latest_only=true&limit=1`,
```

**frontend/src/components/common/ScraperStatusBanner.tsx:**
```javascript
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '';
```

**frontend/src/pages/auth/OAuthCallbackPage.tsx:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';
```

### Frontend .env.production
```env
VITE_API_URL=
VITE_API_BASE_URL=
```
Empty values = same-origin requests (nginx proxies /api to backend)

---

## Issue 4: Docker Path Configuration (CONFIG_DIR)

### Problem
Config files (`sites_config.json`, `bengali_news_styles.json`) not found in Docker.

### Cause
Path calculation in `backend/app/config.py`:
```python
BASE_DIR = Path(__file__).parent.parent  # /app/app → /app
PROJECT_ROOT = BASE_DIR.parent           # /app → / (FILESYSTEM ROOT!)
CONFIG_DIR = PROJECT_ROOT / 'config'     # /config (DOESN'T EXIST!)
```

In Docker, going up from `/app` reaches filesystem root `/`, not the project root.

### Solution
Module-level path detection in `backend/app/config.py`:
```python
_BASE_DIR = Path(__file__).parent.parent
_DOCKER_CONFIG = Path('/app/config')

if _DOCKER_CONFIG.exists():
    _CONFIG_DIR = _DOCKER_CONFIG
    _PROJECT_ROOT = Path('/app')
else:
    _PROJECT_ROOT = _BASE_DIR.parent
    _CONFIG_DIR = _PROJECT_ROOT / 'config'
```

---

## Issue 5: Database Migration (allowed_sites column)

### Error
```
500 Internal Server Error
sqlalchemy.exc.OperationalError: no such column: user_configs.allowed_sites
```

### Cause
New `allowed_sites` column added to UserConfig model but not in database.

### Solution

**For SQLite (local development):**
```sql
ALTER TABLE user_configs ADD COLUMN allowed_sites JSON DEFAULT '[]';
```

**For PostgreSQL (production):**
```sql
ALTER TABLE user_configs ADD COLUMN allowed_sites JSON DEFAULT '[]';
```

Note: PostgreSQL uses single quotes for JSON default, not double quotes.

### Migration Script
`backend/migrations/add_allowed_sites.py`
```bash
python -m migrations.add_allowed_sites
```

---

## Issue 6: Port 80/443 Already in Use

### Error
```
Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint swiftor-frontend: Bind for 0.0.0.0:80 failed: port is already allocated
```

### Cause
Another service (in our case, n8n) was already using ports 80 and 443 on the VPS.

### Diagnosis
```bash
# Find what's using port 80
sudo lsof -i :80

# List all Docker containers and their ports
docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
```

Output showed:
```
NAMES              IMAGE                     PORTS                                    STATUS
n8n-n8n-1          docker.n8n.io/n8nio/n8n   127.0.0.1:5678->5678/tcp                Up 4 weeks
```

### Solution
Instead of stopping n8n, we changed Swiftor to use different ports.

**Modified `docker-compose.yml`:**
```yaml
# Before
frontend:
  ports:
    - "80:80"
    - "443:443"

# After
frontend:
  ports:
    - "8080:80"
```

We removed port 443 because SSL will be handled by the host's nginx reverse proxy later.

### Access
After this change, Swiftor is accessible at:
- `http://46.202.160.112:8080`

### Future SSL Setup
To enable HTTPS with domain swiftor.online, we'll set up nginx on the host as a reverse proxy:
1. Install nginx on host: `apt install nginx`
2. Configure reverse proxy to forward swiftor.online → localhost:8080
3. Use certbot for SSL certificate

---

## Issue 7: Frontend Calling localhost:8000 Instead of Backend

### Error
Browser console shows:
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
localhost:8000/api/auth/login
```

### Cause
Two problems:
1. **`.dockerignore` blocked `frontend/.env.production`**: The pattern `.env.*` with `!.env.production` only un-ignores root `.env.production`, not `frontend/.env.production`
2. **Fallback URL was localhost**: The code `API_URL ?? 'http://localhost:8000'` falls back to localhost when env var is undefined

### Solution

**1. Fix `.dockerignore`:**
```diff
  # Environment files (inject at runtime)
  .env
- .env.*
- !.env.production
+ .env.local
+ .env.development
+ .env.development.local
+ # Keep production env files for build
+ !.env.production
+ !frontend/.env.production
```

**2. Fix `frontend/src/api/axios.ts`:**
```javascript
// In production: use empty string (relative URLs, nginx proxies /api to backend)
// In development: use localhost:8000
const API_URL = import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '');
```

This way:
- **Development**: Uses `http://localhost:8000`
- **Production**: Uses empty string `''` (relative URLs like `/api/auth/login`)
- Nginx proxies `/api/*` requests to `backend:8000`

### Rebuild Required
After fixing, on VPS:
```bash
cd /root/projects/swiftor
git pull origin master
docker compose build --no-cache
docker compose up -d
```

---

## Deployment Commands

### Initial Setup on VPS
```bash
# Clone repository
cd /root/projects
git clone https://github.com/Waseekk/content-transformer.git swiftor
cd swiftor

# Create .env file
nano .env
# Add environment variables (see .env.example)

# Build and start
docker compose build --no-cache
docker compose up -d
```

### Update Deployment
```bash
cd /root/projects/swiftor
git pull origin master
docker compose build --no-cache
docker compose up -d
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
# Or specific service
docker compose restart backend
```

### Check Container Status
```bash
docker compose ps
```

---

## Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://swiftor:your_password@postgres:5432/swiftor
POSTGRES_USER=swiftor
POSTGRES_PASSWORD=your_password
POSTGRES_DB=swiftor

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-your-api-key

# OAuth (optional)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

---

## Common Issues

### Container won't start
```bash
docker compose logs backend
# Check for Python import errors or missing dependencies
```

### Frontend shows blank page
- Check browser console for errors
- Verify VITE_API_URL is correct in .env.production
- Check nginx logs: `docker compose logs frontend`

### API returns 502 Bad Gateway
- Backend container may have crashed
- Check: `docker compose ps` - backend should show "Up"
- Check logs: `docker compose logs backend`

### Database connection error
- Verify PostgreSQL container is running
- Check DATABASE_URL in .env
- Ensure postgres service started before backend

---

## Architecture

```
                    ┌─────────────────┐
                    │   Nginx (80)    │
                    │   Frontend      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        /api/*          /ws/*         Static files
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐                ┌─────────┐
    │ Backend (8000)  │                │  React  │
    │    FastAPI      │                │  Build  │
    └────────┬────────┘                └─────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐    ┌───────────┐
│ Postgres│    │   Redis   │
│  (5432) │    │   (6379)  │
└─────────┘    └───────────┘
```

---

## Files Reference

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-stage build for backend and frontend |
| `docker-compose.yml` | Service orchestration |
| `docker/nginx.conf` | Nginx reverse proxy config |
| `.env` | Environment variables (not in git) |
| `frontend/.env.production` | Frontend production env |

---

## Issue 8: Hostinger Firewall Blocking Connections

### Error
```
curl: (28) Failed to connect to 46.202.160.112 port 8080 after 21041 ms: Could not connect to server
```

- Static page `/` loads sometimes
- API calls `/api/*` always timeout
- Intermittent TCP connection failures

### Cause
Hostinger's VPS firewall (when enabled) blocks connections inconsistently, even with correct rules added.

### Diagnosis
1. Test locally on VPS works:
   ```bash
   curl http://localhost:8080/api/health  # Works!
   ```
2. Test externally fails:
   ```powershell
   curl.exe http://46.202.160.112:8080/api/health  # Timeout!
   ```
3. nginx logs show no `/api/` requests reaching the server

### Solution
**Delete the Hostinger firewall entirely** - the VPS works fine without it.

1. Go to Hostinger hPanel → VPS → Security → Firewall
2. Delete the "swiftor" firewall (trash icon)
3. Test again - should work without firewall

Note: Ubuntu's built-in `ufw` was disabled on this VPS, so there's no local firewall blocking traffic.

---

## Hostinger Account Setup

### Important: Two Separate Accounts

| Account | Purpose | Contains |
|---------|---------|----------|
| **Account 1** | VPS Hosting | Ubuntu 24.04 VPS at `46.202.160.112` |
| **Account 2** | Domain | `swiftor.online` domain registration |

### Why This Matters
- **Firewall settings** → Configure in VPS account (Account 1)
- **DNS settings** → Configure in Domain account (Account 2)
- Don't confuse them when making changes!

### DNS Configuration (After VPS is working)

In **Account 2** (domain account), go to DNS Manager and add:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 46.202.160.112 | 3600 |
| A | www | 46.202.160.112 | 3600 |

This points `swiftor.online` to your VPS.

---

## Current Status & Next Steps

### ✅ Completed
1. Docker containers built and running
2. Backend healthy, database connected
3. Frontend serves static files
4. nginx proxy works internally
5. Port 8080 mapped correctly

### 🔄 In Progress
- Hostinger firewall causing external connection issues
- Need to delete firewall and test

### ⏳ Pending (After Site Works)
1. **Create admin user:**
   ```bash
   docker compose exec backend python -c "
   from app.database import SessionLocal
   from app.models.user import User
   from app.core.security import get_password_hash
   db = SessionLocal()
   admin = User(
       email='admin@swiftor.com',
       username='admin',
       hashed_password=get_password_hash('admin123'),
       is_admin=True,
       is_active=True
   )
   db.add(admin)
   db.commit()
   print('Admin created')
   db.close()
   "
   ```

2. **Run database migration:**
   ```bash
   docker compose exec backend python -m migrations.add_allowed_sites
   ```

3. **Point domain to VPS:**
   - In Account 2 (domain), add A record: `swiftor.online` → `46.202.160.112`

4. **Set up SSL certificate:**
   ```bash
   # On VPS, after domain is pointing
   apt install certbot
   certbot certonly --standalone -d swiftor.online
   ```

5. **Configure nginx for SSL** (update docker/nginx.conf)

---

## Quick Reference Commands

### Check Status
```bash
docker compose ps
docker compose logs backend --tail 20
docker compose logs frontend --tail 20
```

### Restart Services
```bash
docker compose restart backend
docker compose restart frontend
```

### Rebuild After Code Changes
```bash
git pull origin master
docker compose build --no-cache frontend
docker compose up -d frontend
```

### Test API Locally
```bash
curl http://localhost:8080/api/health
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

---

## Issue 9: Hostinger Firewall - External Access Blocked Despite Correct Rules

### Problem
After creating a Hostinger panel firewall with correct allow rules, external access to the VPS is completely blocked. Connection attempts timeout on ALL ports (22, 80, 443, 8080).

### Environment
- **VPS IP**: 46.202.160.112
- **Server Location**: India - Mumbai
- **Hostname**: srv1217751.hstgr.cloud
- **Port**: 8080 (Swiftor frontend)

### What We Verified Works
1. ✅ VPS is running (status: Running in panel)
2. ✅ Docker containers running (4 containers: frontend, backend, postgres, redis)
3. ✅ Port 8080 listening: `ss -tlnp | grep 8080` shows docker-proxy listening
4. ✅ Internal access works: `curl localhost:8080/api/health` returns healthy
5. ✅ UFW disabled: `ufw status` shows inactive
6. ✅ iptables not blocking: INPUT chain policy is ACCEPT
7. ✅ Outbound works: VPS can reach internet (`curl https://api.ipify.org`)

### What Doesn't Work
- ❌ External access from ANY location times out
- ❌ All ports blocked: 22 (SSH), 80, 443, 8080
- ❌ Both IP and hostname access fail

### Hostinger Firewall Configuration
Created firewall named "swiftor" with 5 rules:

| Action | Protocol | Port | Source |
|--------|----------|------|--------|
| Accept | SSH | 22 | Any |
| Accept | HTTP | 80 | Any |
| Accept | HTTPS | 443 | Any |
| Accept | TCP | 8080 | Any |
| Drop | Any | Any | Any |

### Troubleshooting Steps Attempted

1. **Deleted old firewall** - External access still blocked
2. **Created new firewall with allow rules** - Still blocked
3. **Reset firewall configuration** (Settings → Reset firewall configuration) - Still blocked
4. **Verified firewall is "Active"** in panel - Shows active with toggle ON
5. **Checked Incoming traffic metric** - Shows 38.9 MB (some traffic getting through)
6. **Reviewed frontend logs** - Shows some external IPs connected earlier (before firewall creation)

### Nginx Config Fix Applied
Fixed `/api/*` proxy issue:
```nginx
# Changed from:
proxy_pass http://backend/api/;
# To:
proxy_pass http://backend/;
```
This fix works internally - `curl localhost:8080/api/health` now returns healthy.

### Possible Causes
1. **Firewall not properly assigned to VPS** - Even though it shows "Active", it may not be linked to the specific VPS
2. **Hostinger network-level block** - Separate from the panel firewall
3. **Firewall propagation delay** - Rules may take time to apply
4. **Geographic/ISP blocking** - Unlikely since multiple locations tested

### Recommended Next Steps

#### Option 1: Contact Hostinger Support
Contact Hostinger support with this information:
- VPS: srv1217751.hstgr.cloud (46.202.160.112)
- Issue: Cannot access VPS externally on any port despite firewall rules allowing traffic
- Firewall "swiftor" is Active with correct rules
- Internal access works, external doesn't

#### Option 2: Reboot VPS
1. Go to Hostinger panel → VPS Overview
2. Click "Reboot VPS"
3. Wait 3-5 minutes
4. Test access again

#### Option 3: Delete Firewall Completely
1. Go to Security → Firewall
2. Delete the "swiftor" firewall completely
3. Test if traffic flows (some Hostinger VPS work without panel firewall)
4. If works, rely on UFW for security instead

#### Option 4: Use Host-Level Nginx (Port 80/443)
If port 8080 is blocked but standard ports work differently:
1. Stop Traefik/n8n or change their ports
2. Configure Swiftor on port 80 directly
3. This might bypass firewall issues

### Commands for Testing (On VPS)
```bash
# Check firewall status
ufw status

# Check what's listening
ss -tlnp

# Check iptables
iptables -L -n

# Test internal access
curl -s localhost:8080/api/health

# Check Docker containers
docker ps

# View frontend logs for external requests
docker logs swiftor-frontend --tail 50
```

### Commands for Testing (From Local Machine)
```powershell
# Test connection
curl.exe -v --connect-timeout 10 http://46.202.160.112:8080/

# Test port 80
curl.exe -v --connect-timeout 10 http://46.202.160.112/

# Test hostname
curl.exe -v --connect-timeout 10 http://srv1217751.hstgr.cloud:8080/
```

---

## Current Status (2026-01-24)

### ✅ Completed
1. Docker containers built and running
2. Backend healthy, database connected
3. Frontend serves static files
4. Nginx proxy configuration fixed (`/api/*` routes work)
5. Port 8080 mapped correctly
6. Hostinger firewall created with correct rules

### ❌ Blocked
- **External access not working** - Hostinger network issue
- Cannot proceed with domain setup, SSL, or user creation until this is resolved

### ⏳ Pending (After External Access Works)
1. Create admin user
2. Point domain `swiftor.online` to VPS
3. Set up SSL certificate
4. Configure nginx for HTTPS

---

*Last Updated: 2026-01-24*

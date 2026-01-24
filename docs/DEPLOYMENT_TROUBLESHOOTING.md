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

*Last Updated: 2026-01-24*

# VPS Stability & Log Management Guide

This document covers the stability improvements and VPS configuration for Swiftor.

## Quick Setup Commands (Run on VPS)

### 1. Add Traefik Weekly Restart (Prevents Gateway Timeouts)

```bash
# Add to crontab
echo "0 4 * * 0 root cd /docker/n8n && docker compose restart traefik" >> /etc/crontab
```

### 2. Add Docker Log Rotation

```bash
# Create logrotate config for Docker containers
cat > /etc/logrotate.d/docker-containers << 'EOF'
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size 50M
    missingok
    delaycompress
    copytruncate
}
EOF
```

### 3. Add Health Check Cron

```bash
# Copy health check script to VPS
scp scripts/health_check.sh root@your-vps:/root/scripts/

# Make executable
chmod +x /root/scripts/health_check.sh

# Add to crontab (runs every 5 minutes)
echo "*/5 * * * * /root/scripts/health_check.sh >> /var/log/swiftor-health.log 2>&1" >> /etc/crontab
```

### 4. Add Daily Docker Cleanup

```bash
# Add to crontab (runs at 3 AM daily)
echo "0 3 * * * docker system prune -f" >> /etc/crontab
```

### 5. Apply Crontab Changes

```bash
# Restart cron to apply changes
systemctl restart cron
```

---

## What Was Changed in Code

### 1. Docker Compose (`docker-compose.yml`)

**Resource Limits Added:**
- `postgres`: 1G memory, 1 CPU
- `redis`: 256M memory, 0.5 CPU
- `backend`: 2G memory, 2 CPUs
- `frontend`: 512M memory, 1 CPU

**Log Rotation Added:**
- All services now have `max-size` and `max-file` limits
- Backend: 50m x 5 files
- Others: 10-20m x 3 files

### 2. Backend Shutdown Handler (`backend/app/main.py`)

**Before:** Empty shutdown handler
**After:** Properly stops scheduler and disposes database connections

### 3. Playwright Memory Leak (`backend/app/services/playwright_extractor.py`)

**Before:** Browser context was never closed
**After:** Context is now properly closed in finally block

### 4. Caddyfile (`docker/Caddyfile`)

**Added:**
- Reverse proxy timeouts (10s dial, 120s response)
- Health checking for backend
- Static file caching headers (1 year for /assets/*, 1 day for other static files)

### 5. Database Pool (`backend/app/database.py`)

**Added:**
- `pool_recycle=3600` - Recycle connections every hour
- `pool_timeout=30` - 30 second timeout waiting for connection

---

## Verification Commands

### After Docker Changes

```bash
# Redeploy
docker compose down && docker compose up -d

# Check all services are healthy
docker compose ps

# Verify resource limits are applied
docker stats --no-stream

# Check log sizes
du -sh /var/lib/docker/containers/*/
```

### Health Check Verification

```bash
# Test API health
curl -s https://swiftor.online/api/health | jq

# Check container health
docker compose ps

# View recent logs
docker logs swiftor-backend --tail 50

# Test health check script
/root/scripts/health_check.sh
```

### Log Rotation Verification

```bash
# Dry run logrotate
logrotate -d /etc/logrotate.d/docker-containers

# Force rotation (for testing)
logrotate -f /etc/logrotate.d/docker-containers

# Check log sizes after
ls -lh /var/lib/docker/containers/*/*.log
```

---

## Monitoring Disk Space

```bash
# Current disk usage
df -h /

# Docker disk usage
docker system df

# Find large files in Docker
du -sh /var/lib/docker/*

# Clean up unused Docker resources
docker system prune -a --volumes
```

---

## Troubleshooting

### Gateway Timeout (502/504)

1. Check backend health: `docker logs swiftor-backend --tail 50`
2. Check Traefik: `docker logs traefik --tail 50`
3. Restart Traefik: `cd /docker/n8n && docker compose restart traefik`
4. Restart backend: `docker restart swiftor-backend`

### High Memory Usage

1. Check memory: `free -h`
2. Check container memory: `docker stats --no-stream`
3. Restart high-memory container: `docker restart <container>`

### Disk Full

1. Check disk: `df -h`
2. Clean Docker: `docker system prune -f`
3. Clean logs: `journalctl --vacuum-size=100M`
4. Force log rotation: `logrotate -f /etc/logrotate.d/docker-containers`

### Database Connection Issues

1. Check PostgreSQL: `docker logs swiftor-postgres --tail 50`
2. Check connection count: `docker exec swiftor-postgres psql -U swiftor -c "SELECT count(*) FROM pg_stat_activity;"`
3. Restart PostgreSQL: `docker restart swiftor-postgres`

---

## Cron Jobs Summary

| Schedule | Command | Purpose |
|----------|---------|---------|
| `*/5 * * * *` | health_check.sh | Monitor health, auto-restart unhealthy containers |
| `0 3 * * *` | docker system prune -f | Daily Docker cleanup |
| `0 4 * * 0` | restart traefik | Weekly Traefik restart |

---

## Files Modified

| File | Changes |
|------|---------|
| `docker-compose.yml` | Resource limits, logging config |
| `docker/Caddyfile` | Timeouts, health checks, caching |
| `backend/app/main.py` | Proper shutdown handler |
| `backend/app/database.py` | Pool recycling |
| `backend/app/services/playwright_extractor.py` | Context cleanup |
| `scripts/health_check.sh` | New health check script |

# Post-Deployment Monitoring Guide

This document contains all VPS commands and configurations to apply after deploying the stability fixes.

---

## Step 1: Deploy Updated Code

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Navigate to project directory
cd /root/projects/swiftor

# Pull latest changes
git pull origin master

# Rebuild and restart containers
docker compose down
docker compose build --no-cache
docker compose up -d

# Verify all containers are healthy
docker compose ps
```

---

## Step 2: Add Cron Jobs

### Option A: Add All at Once (Recommended)

```bash
# Add all cron jobs in one command
cat >> /etc/crontab << 'EOF'

# ============================================================
# Swiftor Monitoring Cron Jobs
# ============================================================

# Health check every 5 minutes
*/5 * * * * root /root/scripts/health_check.sh >> /var/log/swiftor-health.log 2>&1

# Daily Docker cleanup at 3 AM
0 3 * * * root docker system prune -f >> /var/log/docker-cleanup.log 2>&1

# Weekly Traefik restart (Sunday 4 AM) - prevents gateway timeouts
0 4 * * 0 root cd /docker/n8n && docker compose restart traefik >> /var/log/traefik-restart.log 2>&1

# Weekly journal cleanup (Sunday 5 AM)
0 5 * * 0 root journalctl --vacuum-size=100M >> /var/log/journal-cleanup.log 2>&1

EOF
```

### Option B: Add Individually

```bash
# Health check (every 5 minutes)
echo "*/5 * * * * root /root/scripts/health_check.sh >> /var/log/swiftor-health.log 2>&1" >> /etc/crontab

# Docker cleanup (daily at 3 AM)
echo "0 3 * * * root docker system prune -f >> /var/log/docker-cleanup.log 2>&1" >> /etc/crontab

# Traefik restart (weekly Sunday 4 AM)
echo "0 4 * * 0 root cd /docker/n8n && docker compose restart traefik >> /var/log/traefik-restart.log 2>&1" >> /etc/crontab

# Journal cleanup (weekly Sunday 5 AM)
echo "0 5 * * 0 root journalctl --vacuum-size=100M >> /var/log/journal-cleanup.log 2>&1" >> /etc/crontab
```

### Apply Cron Changes

```bash
# Restart cron service
systemctl restart cron

# Verify cron jobs
crontab -l
cat /etc/crontab | grep swiftor
```

---

## Step 3: Setup Health Check Script

```bash
# Create scripts directory
mkdir -p /root/scripts

# Copy health check script (run from your local machine)
scp scripts/health_check.sh root@your-vps-ip:/root/scripts/

# OR create it directly on VPS
cat > /root/scripts/health_check.sh << 'SCRIPT'
#!/bin/bash
# Swiftor Health Check Script

COMPOSE_FILE="/root/projects/swiftor/docker-compose.yml"
HEALTH_URL="https://swiftor.online/api/health"
DISK_THRESHOLD=85
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

log_info() { echo "${LOG_PREFIX} [INFO] $1"; }
log_warn() { echo "${LOG_PREFIX} [WARN] $1"; }
log_error() { echo "${LOG_PREFIX} [ERROR] $1"; }

# Check containers
check_containers() {
    log_info "Checking containers..."
    UNHEALTHY=$(docker compose -f "$COMPOSE_FILE" ps 2>/dev/null | grep -i unhealthy || true)
    if [ -n "$UNHEALTHY" ]; then
        log_error "Unhealthy containers found"
        docker compose -f "$COMPOSE_FILE" restart
        return 1
    fi
    log_info "All containers healthy"
}

# Check API
check_api() {
    log_info "Checking API..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" != "200" ]; then
        log_error "API health check failed (HTTP $HTTP_CODE)"
        return 1
    fi
    log_info "API OK (HTTP $HTTP_CODE)"
}

# Check disk
check_disk() {
    log_info "Checking disk..."
    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
        log_warn "Disk at ${DISK_USAGE}%, running cleanup..."
        docker system prune -f --volumes 2>/dev/null || true
        return 1
    fi
    log_info "Disk OK: ${DISK_USAGE}%"
}

# Main
log_info "========== Health Check Start =========="
check_containers
check_api
check_disk
log_info "========== Health Check Complete =========="
SCRIPT

# Make executable
chmod +x /root/scripts/health_check.sh

# Test it
/root/scripts/health_check.sh
```

---

## Step 4: Setup Log Rotation

```bash
# Create Docker log rotation config
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

# Create Swiftor monitoring logs rotation
cat > /etc/logrotate.d/swiftor-monitoring << 'EOF'
/var/log/swiftor-*.log /var/log/docker-*.log /var/log/traefik-*.log {
    rotate 4
    weekly
    compress
    missingok
    notifempty
    create 0640 root root
}
EOF

# Test logrotate config (dry run)
logrotate -d /etc/logrotate.d/docker-containers
logrotate -d /etc/logrotate.d/swiftor-monitoring
```

---

## Step 5: Verify Everything

### Container Health

```bash
# Check all containers are running and healthy
docker compose ps

# Expected output:
# NAME               STATUS                   PORTS
# swiftor-backend    Up X minutes (healthy)
# swiftor-frontend   Up X minutes             0.0.0.0:8080->80/tcp
# swiftor-postgres   Up X minutes (healthy)
# swiftor-redis      Up X minutes (healthy)
```

### Resource Limits

```bash
# Verify resource limits are applied
docker stats --no-stream

# Check memory limits
docker inspect swiftor-backend | grep -A5 "Memory"
```

### API Health

```bash
# Test health endpoint
curl -s https://swiftor.online/api/health | jq

# Expected:
# {
#   "status": "healthy",
#   "database": "connected",
#   "services": { ... }
# }
```

### Log Sizes

```bash
# Check Docker log sizes
du -sh /var/lib/docker/containers/*/*.log

# Check total Docker disk usage
docker system df
```

### Cron Jobs

```bash
# List all cron jobs
cat /etc/crontab | grep -E "(swiftor|docker|traefik)"

# Check cron service
systemctl status cron
```

---

## Daily Monitoring Commands

### Quick Health Check

```bash
# One-liner to check everything
docker compose ps && curl -s https://swiftor.online/api/health | jq '.status' && df -h / | tail -1
```

### View Recent Logs

```bash
# Backend logs (last 50 lines)
docker logs swiftor-backend --tail 50

# Health check logs
tail -50 /var/log/swiftor-health.log

# All container logs combined
docker compose logs --tail 20
```

### Resource Usage

```bash
# Live resource monitoring
docker stats

# Snapshot
docker stats --no-stream
```

---

## Troubleshooting Playbook

### Problem: Gateway Timeout (502/504)

```bash
# 1. Check backend status
docker logs swiftor-backend --tail 100

# 2. Check Traefik
docker logs traefik --tail 50

# 3. Restart in order
docker restart swiftor-backend
sleep 10
cd /docker/n8n && docker compose restart traefik
```

### Problem: High Memory

```bash
# 1. Check memory
free -h
docker stats --no-stream

# 2. Find culprit and restart
docker restart swiftor-backend  # Usually the culprit
```

### Problem: Disk Full

```bash
# 1. Check usage
df -h /
du -sh /var/lib/docker/*

# 2. Aggressive cleanup
docker system prune -a --volumes -f
journalctl --vacuum-size=50M

# 3. Force log rotation
logrotate -f /etc/logrotate.d/docker-containers
```

### Problem: Database Connection Errors

```bash
# 1. Check PostgreSQL
docker logs swiftor-postgres --tail 50

# 2. Check connection count
docker exec swiftor-postgres psql -U swiftor -c "SELECT count(*) FROM pg_stat_activity;"

# 3. Restart if needed
docker restart swiftor-postgres
sleep 5
docker restart swiftor-backend
```

---

## Monitoring Checklist

Run weekly:

- [ ] Check disk usage: `df -h /`
- [ ] Check Docker disk: `docker system df`
- [ ] Review health logs: `tail -100 /var/log/swiftor-health.log`
- [ ] Check container restarts: `docker compose ps`
- [ ] Verify API response time: `curl -w "%{time_total}s\n" -o /dev/null -s https://swiftor.online/api/health`

---

## Summary of Cron Schedule

| Time | Frequency | Task |
|------|-----------|------|
| */5 * * * * | Every 5 min | Health check |
| 0 3 * * * | Daily 3 AM | Docker cleanup |
| 0 4 * * 0 | Sunday 4 AM | Traefik restart |
| 0 5 * * 0 | Sunday 5 AM | Journal cleanup |

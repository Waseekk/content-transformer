#!/bin/bash
# ============================================================
# Swiftor Health Check Script
# Run via cron: */5 * * * * /root/scripts/health_check.sh >> /var/log/swiftor-health.log 2>&1
# ============================================================

set -e

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-/root/projects/swiftor/docker-compose.yml}"
HEALTH_URL="${HEALTH_URL:-https://swiftor.online/api/health}"
DISK_THRESHOLD=85
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M:%S')]"

# Colors for output (when running interactively)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo "${LOG_PREFIX} [INFO] $1"
}

log_warn() {
    echo "${LOG_PREFIX} [WARN] $1"
}

log_error() {
    echo "${LOG_PREFIX} [ERROR] $1"
}

# Check if containers are healthy
check_containers() {
    log_info "Checking container health..."

    # Get list of unhealthy containers
    UNHEALTHY=$(docker compose -f "$COMPOSE_FILE" ps --format json 2>/dev/null | jq -r 'select(.Health == "unhealthy") | .Name' 2>/dev/null || true)

    if [ -n "$UNHEALTHY" ]; then
        log_error "Unhealthy containers found: $UNHEALTHY"

        # Restart unhealthy containers
        for container in $UNHEALTHY; do
            log_warn "Restarting unhealthy container: $container"
            docker restart "$container" || true
        done

        return 1
    fi

    log_info "All containers are healthy"
    return 0
}

# Check API health endpoint
check_api() {
    log_info "Checking API health endpoint..."

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        log_info "API health check passed (HTTP $HTTP_CODE)"
        return 0
    else
        log_error "API health check failed (HTTP $HTTP_CODE)"
        return 1
    fi
}

# Check disk usage
check_disk() {
    log_info "Checking disk usage..."

    DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
        log_warn "Disk usage at ${DISK_USAGE}% (threshold: ${DISK_THRESHOLD}%)"

        # Clean up Docker resources
        log_info "Running Docker cleanup..."
        docker system prune -f --volumes 2>/dev/null || true

        # Clean old logs
        log_info "Cleaning old journal logs..."
        journalctl --vacuum-size=100M 2>/dev/null || true

        # Report new usage
        NEW_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
        log_info "Disk usage after cleanup: ${NEW_USAGE}%"

        return 1
    fi

    log_info "Disk usage OK: ${DISK_USAGE}%"
    return 0
}

# Check memory usage
check_memory() {
    log_info "Checking memory usage..."

    # Get memory usage percentage
    MEM_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')

    if [ "$MEM_USAGE" -gt 90 ]; then
        log_warn "Memory usage critical: ${MEM_USAGE}%"

        # Show top memory consumers
        log_info "Top memory consumers:"
        docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" 2>/dev/null | head -5

        return 1
    fi

    log_info "Memory usage OK: ${MEM_USAGE}%"
    return 0
}

# Main execution
main() {
    log_info "========== Starting Swiftor health check =========="

    ERRORS=0

    check_containers || ((ERRORS++))
    check_api || ((ERRORS++))
    check_disk || ((ERRORS++))
    check_memory || ((ERRORS++))

    if [ "$ERRORS" -gt 0 ]; then
        log_warn "Health check completed with $ERRORS warning(s)"
        exit 1
    else
        log_info "Health check completed successfully"
        exit 0
    fi
}

main "$@"

#!/bin/bash
# Health check script for code_developer daemon container
# Used by Docker/Kubernetes to verify daemon is healthy

set -e

# Configuration
API_HOST="${API_HOST:-localhost}"
API_PORT="${API_PORT:-8080}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/api/health}"
TIMEOUT=5

# Colors for output (if terminal supports it)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_info() {
    echo -e "${GREEN}[HEALTH]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[HEALTH]${NC} $1"
}

log_error() {
    echo -e "${RED}[HEALTH]${NC} $1"
}

# Check if API is responsive
check_api_health() {
    local url="http://${API_HOST}:${API_PORT}${HEALTH_ENDPOINT}"

    response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" = "200" ]; then
        log_info "API health check passed (HTTP $http_code)"
        return 0
    else
        log_error "API health check failed (HTTP $http_code)"
        return 1
    fi
}

# Check if daemon process is running (if applicable)
check_daemon_process() {
    # Check if Python process is running
    if pgrep -f "python.*coffee_maker" > /dev/null; then
        log_info "Daemon process is running"
        return 0
    else
        log_warn "Daemon process not found"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local threshold=90
    local usage=$(df -h /workspace 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ -n "$usage" ]; then
        if [ "$usage" -lt "$threshold" ]; then
            log_info "Disk space OK ($usage% used)"
            return 0
        else
            log_error "Disk space critical ($usage% used, threshold: $threshold%)"
            return 1
        fi
    else
        log_warn "Could not check disk space"
        return 0  # Don't fail health check if we can't check
    fi
}

# Check memory usage
check_memory() {
    local threshold=90
    local mem_info=$(free | grep Mem)
    local total=$(echo $mem_info | awk '{print $2}')
    local used=$(echo $mem_info | awk '{print $3}')

    if [ "$total" -gt 0 ]; then
        local usage=$((used * 100 / total))
        if [ "$usage" -lt "$threshold" ]; then
            log_info "Memory usage OK ($usage% used)"
            return 0
        else
            log_warn "Memory usage high ($usage% used, threshold: $threshold%)"
            return 0  # Warning but don't fail
        fi
    else
        return 0
    fi
}

# Main health check logic
main() {
    log_info "Starting health check..."

    local exit_code=0

    # Primary check: API health
    if ! check_api_health; then
        exit_code=1
    fi

    # Secondary checks (warnings only)
    check_daemon_process || true
    check_disk_space || true
    check_memory || true

    if [ $exit_code -eq 0 ]; then
        log_info "Health check completed: HEALTHY"
        exit 0
    else
        log_error "Health check completed: UNHEALTHY"
        exit 1
    fi
}

# Run main function
main "$@"

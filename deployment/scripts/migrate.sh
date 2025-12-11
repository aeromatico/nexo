#!/bin/bash
# Nexo Database Migration Script
# Usage: ./migrate.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
LOG_FILE="migration-$(date +%Y%m%d-%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_info "Starting database migrations for $ENVIRONMENT..."
log_info "Log file: $LOG_FILE"

# Check if bench command exists
if ! command -v bench &> /dev/null; then
    log_warn "Bench not found in PATH, checking docker-compose..."

    if ! command -v docker-compose &> /dev/null; then
        log_error "Neither bench nor docker-compose found"
        exit 1
    fi

    # Using docker-compose
    log_info "Running migrations with docker-compose..."

    cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T erpnext \
        bash -c "bench --site \$(ls sites/ | head -1) migrate" >> "$LOG_FILE" 2>&1

else
    # Using bench directly
    log_info "Running migrations with bench..."

    cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

    # Find sites
    SITES=$(bench find-sites)

    for site in $SITES; do
        log_info "Migrating site: $site"
        bench --site "$site" migrate >> "$LOG_FILE" 2>&1 || {
            log_error "Migration failed for site: $site"
            exit 1
        }
    done
fi

# Additional migration tasks
log_info "Running post-migration tasks..."

# Update hooks
log_info "Updating hooks..."
if command -v bench &> /dev/null; then
    bench build >> "$LOG_FILE" 2>&1 || true
fi

# Clear cache
log_info "Clearing caches..."
docker-compose -f deployment/docker/docker-compose.prod.yml exec -T redis-cache \
    redis-cli FLUSHDB >> "$LOG_FILE" 2>&1 || true

# Verify migration
log_info "Verifying migration..."

if command -v bench &> /dev/null; then
    SITES=$(bench find-sites)
    for site in $SITES; do
        log_info "Checking site: $site"
        bench --site "$site" execute "frappe.db.get_list('DocType', limit_page_length=1)" >> "$LOG_FILE" 2>&1 || {
            log_error "Verification failed for site: $site"
            exit 1
        }
    done
fi

log_info "=========================================="
log_info "Database migrations completed successfully!"
log_info "Log file: $LOG_FILE"
log_info "=========================================="

exit 0

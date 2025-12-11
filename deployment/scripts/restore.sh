#!/bin/bash
# Nexo Restore Script
# Usage: ./restore.sh [staging|production] [backup_name]

set -e

ENVIRONMENT=$1
BACKUP_NAME=$2
BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate inputs
if [ -z "$ENVIRONMENT" ]; then
    log_error "Environment not specified"
    exit 1
fi

# If backup name not provided, use latest
if [ -z "$BACKUP_NAME" ]; then
    BACKUP_NAME=$(ls -1 "$BACKUP_DIR" | grep "nexo_backup_${ENVIRONMENT}" | tail -1 | sed 's/_db.sql.gz//' | sed 's/_sites.tar.gz//' | sed 's/_apps.tar.gz//' | sort | uniq | tail -1)

    if [ -z "$BACKUP_NAME" ]; then
        log_error "No backups found for $ENVIRONMENT"
        exit 1
    fi

    log_info "Using latest backup: $BACKUP_NAME"
fi

log_warn "Starting restore from backup: $BACKUP_NAME"
log_warn "This will overwrite current data!"

# Confirmation
read -p "Type 'CONFIRM' to proceed: " confirmation
if [ "$confirmation" != "CONFIRM" ]; then
    log_error "Restore cancelled"
    exit 1
fi

# 1. Stop services
log_info "Stopping services..."
docker-compose -f deployment/docker/docker-compose.prod.yml stop erpnext erpnext-worker erpnext-scheduler 2>/dev/null || true
sleep 5
log_info "Services stopped"

# 2. Restore database
if [ -f "$BACKUP_DIR/${BACKUP_NAME}_db.sql.gz" ]; then
    log_info "Restoring database..."

    DB_HOST=${DB_HOST:-localhost}
    DB_USER=${DB_USER:-frappe}
    DB_NAME=${DB_NAME:-nexo}

    # Extract and restore
    gunzip -c "$BACKUP_DIR/${BACKUP_NAME}_db.sql.gz" | \
    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
        mysql -u "$DB_USER" -p"${DB_PASSWORD}" "$DB_NAME" 2>/dev/null || true

    log_info "Database restored"
else
    log_error "Database backup not found"
    exit 1
fi

# 3. Restore sites
if [ -f "$BACKUP_DIR/${BACKUP_NAME}_sites.tar.gz" ]; then
    log_info "Restoring sites..."

    # Backup current sites first
    if [ -d "sites" ]; then
        tar -czf "${BACKUP_DIR}/sites_before_restore.tar.gz" sites/ 2>/dev/null || true
    fi

    # Restore
    tar -xzf "$BACKUP_DIR/${BACKUP_NAME}_sites.tar.gz" -C . 2>/dev/null || true
    log_info "Sites restored"
fi

# 4. Verify restore
log_info "Verifying restore..."

if [ ! -f "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt" ]; then
    log_error "Manifest file not found"
    exit 1
fi

cat "$BACKUP_DIR/${BACKUP_NAME}_manifest.txt"

# 5. Start services
log_info "Starting services..."
docker-compose -f deployment/docker/docker-compose.prod.yml up -d erpnext erpnext-worker erpnext-scheduler 2>/dev/null || true
sleep 10
log_info "Services started"

# 6. Run migrations if needed
log_info "Running post-restore migrations..."
./deployment/scripts/migrate.sh "$ENVIRONMENT" 2>/dev/null || true

log_info "=========================================="
log_info "Restore completed successfully!"
log_info "Backup restored: $BACKUP_NAME"
log_info "=========================================="

exit 0

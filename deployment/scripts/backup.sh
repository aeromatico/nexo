#!/bin/bash
# Nexo Backup Script
# Usage: ./backup.sh [staging|production|manual]

set -e

ENVIRONMENT=${1:-manual}
BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="nexo_backup_${ENVIRONMENT}_${TIMESTAMP}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log_info "Starting backup: $BACKUP_NAME"

# 1. Database backup
log_info "Backing up database..."

if command -v mysqldump &> /dev/null; then
    DB_HOST=${DB_HOST:-localhost}
    DB_USER=${DB_USER:-frappe}
    DB_NAME=${DB_NAME:-nexo}
    DB_BACKUP="$BACKUP_DIR/${BACKUP_NAME}_db.sql"

    mysqldump -h "$DB_HOST" -u "$DB_USER" -p"${DB_PASSWORD}" \
        --single-transaction --quick --lock-tables=false \
        "$DB_NAME" > "$DB_BACKUP" 2>&1

    log_info "Database backup saved to $DB_BACKUP"
    gzip "$DB_BACKUP"
    log_info "Database backup compressed"
else
    # Use docker-compose for database backup
    BACKUP_PATH="/tmp/${BACKUP_NAME}_db.sql"
    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
        mysqldump --single-transaction --quick --lock-tables=false \
        -u "${DB_USER:-frappe}" -p"${DB_PASSWORD}" \
        "${DB_NAME:-nexo}" > "$BACKUP_DIR/${BACKUP_NAME}_db.sql" 2>&1

    gzip "$BACKUP_DIR/${BACKUP_NAME}_db.sql"
    log_info "Database backup completed"
fi

# 2. Sites backup (files and configurations)
log_info "Backing up sites and files..."

if [ -d "sites" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_sites.tar.gz" sites/ 2>/dev/null || true
    log_info "Sites backup saved"
fi

# 3. Applications backup
log_info "Backing up applications..."

tar -czf "$BACKUP_DIR/${BACKUP_NAME}_apps.tar.gz" \
    apps/nexo_core/ \
    apps/nexo_bolivia/ \
    2>/dev/null || true

log_info "Applications backup saved"

# 4. Configuration backup
log_info "Backing up configurations..."

if [ -d ".env" ] || [ -f ".env" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" .env 2>/dev/null || true
fi

if [ -d "deployment/docker/ssl" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_ssl.tar.gz" deployment/docker/ssl/ 2>/dev/null || true
    log_info "SSL certificates backup saved"
fi

# 5. Create backup manifest
log_info "Creating backup manifest..."

MANIFEST="$BACKUP_DIR/${BACKUP_NAME}_manifest.txt"
{
    echo "Nexo Backup Manifest"
    echo "==================="
    echo "Environment: $ENVIRONMENT"
    echo "Timestamp: $TIMESTAMP"
    echo "Backup Name: $BACKUP_NAME"
    echo ""
    echo "Files:"
    ls -lh "$BACKUP_DIR/${BACKUP_NAME}"* 2>/dev/null | awk '{print $9, "-", $5}'
    echo ""
    echo "Database: $(ls -lh $BACKUP_DIR/${BACKUP_NAME}_db.sql.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')"
    echo "Sites: $(ls -lh $BACKUP_DIR/${BACKUP_NAME}_sites.tar.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')"
    echo "Apps: $(ls -lh $BACKUP_DIR/${BACKUP_NAME}_apps.tar.gz 2>/dev/null | awk '{print $5}' || echo 'N/A')"
    echo ""
    echo "Backup Verification:"
    echo "- Database: $(gzip -t $BACKUP_DIR/${BACKUP_NAME}_db.sql.gz 2>&1 && echo 'OK' || echo 'FAILED')"
} > "$MANIFEST"

log_info "Manifest saved to $MANIFEST"

# 6. Cleanup old backups (keep last 10)
log_info "Cleaning up old backups..."

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | grep "nexo_backup_${ENVIRONMENT}" | wc -l)

if [ "$BACKUP_COUNT" -gt 10 ]; then
    REMOVE_COUNT=$((BACKUP_COUNT - 10))
    ls -1 "$BACKUP_DIR" | grep "nexo_backup_${ENVIRONMENT}" | head -n "$REMOVE_COUNT" | while read -r old_backup; do
        log_info "Removing old backup: $old_backup"
        rm -f "$BACKUP_DIR/$old_backup"*
    done
fi

log_info "=========================================="
log_info "Backup completed successfully!"
log_info "Backup location: $BACKUP_DIR"
log_info "Backup name: $BACKUP_NAME"
log_info "=========================================="

exit 0

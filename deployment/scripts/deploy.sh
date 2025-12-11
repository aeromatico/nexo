#!/bin/bash
# Nexo Deployment Script
# Usage: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=${1:-staging}
LOG_FILE="deployment-$(date +%Y%m%d-%H%M%S).log"
NEXO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Colors for output
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

log_info "Starting deployment to $ENVIRONMENT..."
log_info "Log file: $LOG_FILE"

# Validate environment
if [ "$ENVIRONMENT" != "staging" ] && [ "$ENVIRONMENT" != "production" ]; then
    log_error "Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

cd "$NEXO_DIR"

# 1. Pre-deployment checks
log_info "Running pre-deployment checks..."

if [ ! -d "apps/nexo_core" ]; then
    log_error "nexo_core app not found"
    exit 1
fi

if [ ! -d "apps/nexo_bolivia" ]; then
    log_error "nexo_bolivia app not found"
    exit 1
fi

log_info "Pre-deployment checks passed"

# 2. Backup current deployment
log_info "Creating backup before deployment..."
./deployment/scripts/backup.sh "$ENVIRONMENT" >> "$LOG_FILE" 2>&1
log_info "Backup completed"

# 3. Update code
log_info "Updating code from repository..."
git fetch origin >> "$LOG_FILE" 2>&1

BRANCH=$([ "$ENVIRONMENT" = "production" ] && echo "main" || echo "develop")
git checkout $BRANCH >> "$LOG_FILE" 2>&1
git pull origin $BRANCH >> "$LOG_FILE" 2>&1
log_info "Code updated to latest commit"

# 4. Update dependencies
log_info "Updating dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt >> "$LOG_FILE" 2>&1
fi
log_info "Dependencies updated"

# 5. Database migrations
log_info "Running database migrations..."
./deployment/scripts/migrate.sh "$ENVIRONMENT" >> "$LOG_FILE" 2>&1
log_info "Migrations completed"

# 6. Build assets
log_info "Building assets..."
if command -v bench &> /dev/null; then
    bench build >> "$LOG_FILE" 2>&1
fi
log_info "Assets built"

# 7. Restart services
log_info "Restarting services..."

if [ "$ENVIRONMENT" = "production" ]; then
    log_warn "Production deployment - Using docker-compose"
    cd "$NEXO_DIR/deployment/docker"
    docker-compose -f docker-compose.prod.yml up -d >> "$LOG_FILE" 2>&1
else
    log_info "Staging deployment - Using docker-compose"
    cd "$NEXO_DIR/deployment/docker"
    docker-compose -f docker-compose.prod.yml restart >> "$LOG_FILE" 2>&1
fi

log_info "Services restarted"

# 8. Health checks
log_info "Running health checks..."
if ! ./deployment/scripts/health_check.sh "$ENVIRONMENT" >> "$LOG_FILE" 2>&1; then
    log_error "Health checks failed! Rolling back..."
    ./deployment/scripts/restore.sh "$ENVIRONMENT" >> "$LOG_FILE" 2>&1
    exit 1
fi
log_info "Health checks passed"

# 9. Post-deployment verification
log_info "Running post-deployment verification..."

# Check if services are responding
for i in {1..30}; do
    if curl -sf http://localhost:8000/api/method/ping > /dev/null 2>&1; then
        log_info "Services responding to requests"
        break
    fi
    log_warn "Waiting for services to be ready... ($i/30)"
    sleep 1
done

log_info "=========================================="
log_info "Deployment to $ENVIRONMENT completed successfully!"
log_info "Log file: $LOG_FILE"
log_info "=========================================="

exit 0

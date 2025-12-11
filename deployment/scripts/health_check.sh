#!/bin/bash
# Nexo Health Check Script
# Usage: ./health_check.sh [staging|production|all]

ENVIRONMENT=${1:-all}
SITE_URL=${2:-http://localhost:8000}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

log_fail() {
    echo -e "${RED}✗${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo "ℹ $1"
}

FAILED=0
PASSED=0

echo "=========================================="
echo "Nexo Health Check - $ENVIRONMENT"
echo "=========================================="
echo ""

# 1. Check HTTP/HTTPS connectivity
log_info "Checking HTTP connectivity..."
if curl -sf "$SITE_URL/health" > /dev/null 2>&1; then
    log_pass "HTTP connectivity"
    ((PASSED++))
else
    log_fail "HTTP connectivity"
    ((FAILED++))
fi

# 2. Check API endpoint
log_info "Checking API endpoint..."
if curl -sf "$SITE_URL/api/method/ping" > /dev/null 2>&1; then
    log_pass "API endpoint"
    ((PASSED++))
else
    log_fail "API endpoint"
    ((FAILED++))
fi

# 3. Check database
log_info "Checking database..."
if command -v mysqladmin &> /dev/null; then
    if mysqladmin -h "${DB_HOST:-localhost}" -u "${DB_USER:-frappe}" -p"${DB_PASSWORD}" ping > /dev/null 2>&1; then
        log_pass "Database connectivity"
        ((PASSED++))
    else
        log_fail "Database connectivity"
        ((FAILED++))
    fi
else
    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T mariadb \
        mysqladmin -u "${DB_USER:-frappe}" -p"${DB_PASSWORD}" ping > /dev/null 2>&1 && \
    { log_pass "Database connectivity"; ((PASSED++)); } || \
    { log_fail "Database connectivity"; ((FAILED++)); }
fi

# 4. Check Redis cache
log_info "Checking Redis cache..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h "${REDIS_CACHE_HOST:-localhost}" ping 2>/dev/null | grep -q PONG; then
        log_pass "Redis cache"
        ((PASSED++))
    else
        log_fail "Redis cache"
        ((FAILED++))
    fi
else
    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T redis-cache \
        redis-cli ping > /dev/null 2>&1 && \
    { log_pass "Redis cache"; ((PASSED++)); } || \
    { log_fail "Redis cache"; ((FAILED++)); }
fi

# 5. Check Redis queue
log_info "Checking Redis queue..."
if command -v redis-cli &> /dev/null; then
    if redis-cli -h "${REDIS_QUEUE_HOST:-localhost}" ping 2>/dev/null | grep -q PONG; then
        log_pass "Redis queue"
        ((PASSED++))
    else
        log_fail "Redis queue"
        ((FAILED++))
    fi
else
    docker-compose -f deployment/docker/docker-compose.prod.yml exec -T redis-queue \
        redis-cli ping > /dev/null 2>&1 && \
    { log_pass "Redis queue"; ((PASSED++)); } || \
    { log_fail "Redis queue"; ((FAILED++)); }
fi

# 6. Check Nexo applications
log_info "Checking Nexo applications..."
if curl -sf "$SITE_URL/api/resource/Company" > /dev/null 2>&1; then
    log_pass "Nexo Core API"
    ((PASSED++))
else
    log_fail "Nexo Core API"
    ((FAILED++))
fi

# 7. Check SIN integration (if enabled)
log_info "Checking SIN integration..."
if curl -sf "$SITE_URL/api/method/nexo_bolivia.sin_integration.check_status" > /dev/null 2>&1; then
    log_pass "SIN integration"
    ((PASSED++))
else
    log_warn "SIN integration (may be disabled)"
    ((PASSED++))
fi

# 8. Check E-commerce module (if enabled)
log_info "Checking E-commerce module..."
if curl -sf "$SITE_URL/api/method/nexo_core.ecommerce.check_status" > /dev/null 2>&1; then
    log_pass "E-commerce module"
    ((PASSED++))
else
    log_warn "E-commerce module (may be disabled)"
    ((PASSED++))
fi

# 9. Check Payroll module (if enabled)
log_info "Checking Payroll module..."
if curl -sf "$SITE_URL/api/method/nexo_bolivia.payroll.check_status" > /dev/null 2>&1; then
    log_pass "Payroll module"
    ((PASSED++))
else
    log_warn "Payroll module (may be disabled)"
    ((PASSED++))
fi

# 10. Check disk space
log_info "Checking disk space..."
DISK_USAGE=$(df / | awk 'NR==2 {print int($5)}')
if [ "$DISK_USAGE" -lt 90 ]; then
    log_pass "Disk space (${DISK_USAGE}% used)"
    ((PASSED++))
else
    log_fail "Disk space (${DISK_USAGE}% used - WARNING)"
    ((FAILED++))
fi

# 11. Check memory
log_info "Checking memory..."
if command -v free &> /dev/null; then
    MEMORY_USAGE=$(free | awk 'NR==2 {print int($3/$2 * 100)}')
    if [ "$MEMORY_USAGE" -lt 90 ]; then
        log_pass "Memory (${MEMORY_USAGE}% used)"
        ((PASSED++))
    else
        log_fail "Memory (${MEMORY_USAGE}% used - WARNING)"
        ((FAILED++))
    fi
fi

# 12. Check Docker containers
log_info "Checking Docker containers..."
if command -v docker &> /dev/null; then
    RUNNING=$(docker-compose -f deployment/docker/docker-compose.prod.yml ps -q | wc -l)
    TOTAL=$(docker-compose -f deployment/docker/docker-compose.prod.yml config --services | wc -l)

    if [ "$RUNNING" -eq "$TOTAL" ]; then
        log_pass "Docker containers ($RUNNING/$TOTAL running)"
        ((PASSED++))
    else
        log_fail "Docker containers ($RUNNING/$TOTAL running)"
        ((FAILED++))
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "Health Check Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "=========================================="

if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi

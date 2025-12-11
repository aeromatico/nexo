#!/bin/bash
set -e

echo "========================================"
echo "Building Nexo Frontend Applications"
echo "========================================"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
APPS_DIR="$PROJECT_ROOT/apps/nexo_core/nexo_core"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Building Customer Portal...${NC}"
cd "$FRONTEND_DIR/customer-portal"
npm install 2>/dev/null || true
npm run build
mkdir -p "$APPS_DIR/public/portal"
cp -r dist/* "$APPS_DIR/public/portal/" || true
echo -e "${GREEN}✓ Customer Portal built${NC}"

echo -e "${BLUE}Building E-commerce Store...${NC}"
cd "$FRONTEND_DIR/ecommerce-store"
npm install 2>/dev/null || true
npm run build
mkdir -p "$APPS_DIR/public/store"
cp -r dist/* "$APPS_DIR/public/store/" || true
echo -e "${GREEN}✓ E-commerce Store built${NC}"

echo -e "${BLUE}Building Admin Dashboard...${NC}"
cd "$FRONTEND_DIR/admin-dashboard"
npm install 2>/dev/null || true
npm run build
mkdir -p "$APPS_DIR/public/admin"
cp -r dist/* "$APPS_DIR/public/admin/" || true
echo -e "${GREEN}✓ Admin Dashboard built${NC}"

echo -e "${GREEN}========================================"
echo "All frontend apps built successfully!"
echo "=======================================${NC}"

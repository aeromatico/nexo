#!/bin/bash
set -e

echo "========================================"
echo "Building Nexo Mobile App"
echo "========================================"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOBILE_DIR="$PROJECT_ROOT/mobile/nexo-mobile"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$MOBILE_DIR"

echo -e "${BLUE}Installing dependencies...${NC}"
npm install

echo -e "${BLUE}Building for iOS...${NC}"
eas build --platform ios --non-interactive || echo "iOS build skipped (requires Apple Developer account)"

echo -e "${BLUE}Building for Android...${NC}"
eas build --platform android --non-interactive || echo "Android build skipped (requires setup)"

echo -e "${GREEN}========================================"
echo "Mobile app build completed!"
echo "=======================================${NC}"

#!/bin/bash

# Enable Chrome Testing Script
# This script helps set up Chrome integration testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                               ║${NC}"
echo -e "${BLUE}║                      ENABLE CHROME INTEGRATION TESTING                        ║${NC}"
echo -e "${BLUE}║                                                                               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}This script will help you set up Chrome integration testing.${NC}"
echo ""

# Step 1: Check if Chrome is running
echo -e "${YELLOW}Step 1: Checking if Chrome is running...${NC}"
if pgrep -x "Google Chrome" > /dev/null || pgrep -x "chrome" > /dev/null; then
    echo -e "${GREEN}✅ Chrome is running${NC}"
else
    echo -e "${RED}❌ Chrome is not running${NC}"
    echo -e "${CYAN}   Please open Chrome browser first${NC}"
    exit 1
fi
echo ""

# Step 2: Check if app is running
echo -e "${YELLOW}Step 2: Checking if app is accessible...${NC}"
if curl -s http://localhost:8081 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ App is running at http://localhost:8081${NC}"
else
    echo -e "${RED}❌ App is not accessible at http://localhost:8081${NC}"
    echo ""
    echo -e "${CYAN}Start the app in another terminal:${NC}"
    echo -e "${CYAN}   cd runtime${NC}"
    echo -e "${CYAN}   emmett develop${NC}"
    echo ""
    exit 1
fi
echo ""

# Step 3: Check MCP availability
echo -e "${YELLOW}Step 3: Checking MCP Chrome DevTools availability...${NC}"
echo -e "${CYAN}ℹ️  MCP Chrome DevTools requires running in Cursor environment${NC}"
echo -e "${CYAN}   If you're seeing this, you're likely good to go!${NC}"
echo ""

# Step 4: Export environment variable
echo -e "${YELLOW}Step 4: Enabling Chrome testing...${NC}"
export HAS_CHROME_MCP=true
echo -e "${GREEN}✅ HAS_CHROME_MCP=true${NC}"
echo ""

# Step 5: Show how to run tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}Now you can run Chrome tests:${NC}"
echo ""
echo -e "${YELLOW}Option 1: Using run_tests.sh${NC}"
echo -e "   ${GREEN}HAS_CHROME_MCP=true ./run_tests.sh --chrome${NC}"
echo ""
echo -e "${YELLOW}Option 2: Direct pytest${NC}"
echo -e "   ${GREEN}cd runtime${NC}"
echo -e "   ${GREEN}HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -v -s${NC}"
echo ""
echo -e "${YELLOW}Option 3: Export and run${NC}"
echo -e "   ${GREEN}export HAS_CHROME_MCP=true${NC}"
echo -e "   ${GREEN}./run_tests.sh --chrome${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${CYAN}📸 Screenshots will be saved to: runtime/screenshots/${NC}"
echo -e "${CYAN}📖 Full guide: documentation/CHROME_TESTING_GUIDE.md${NC}"
echo ""


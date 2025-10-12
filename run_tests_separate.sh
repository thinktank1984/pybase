#!/bin/bash
# Run each integration test suite separately and save output to individual files
# This script runs tests in Docker and captures output using pipeline operators

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Running All 11 Integration Test Suites"
echo "=========================================="
echo ""

# Create output directory if it doesn't exist
OUTPUT_DIR="test_results"
mkdir -p "$OUTPUT_DIR"

# Timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${YELLOW}[1/11]${NC} Running tests.py (main integration tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/tests.py -v --tb=short \
    > "${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt" 2>&1
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[2/11]${NC} Running test_oauth_real.py (OAuth integration tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_oauth_real.py -v --tb=short \
    > "${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt" 2>&1
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[3/11]${NC} Running test_roles_integration.py (roles & permissions tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_roles_integration.py -v --tb=short \
    > "${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt" 2>&1
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[4/11]${NC} Running test_auto_ui.py (auto UI generation tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_auto_ui.py -v --tb=short \
    > "${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt" 2>&1
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[5/11]${NC} Running test_ui_chrome_real.py (Chrome UI tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_ui_chrome_real.py -v --tb=short \
    > "${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[6/11]${NC} Running test_auth_comprehensive.py (comprehensive auth tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_auth_comprehensive.py -v --tb=short \
    > "${OUTPUT_DIR}/06_auth_comprehensive_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/06_auth_comprehensive_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[7/11]${NC} Running test_model_utils.py (model utility tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_model_utils.py -v --tb=short \
    > "${OUTPUT_DIR}/07_model_utils_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/07_model_utils_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[8/11]${NC} Running test_roles_rest_api.py (roles REST API tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_roles_rest_api.py -v --tb=short \
    > "${OUTPUT_DIR}/08_roles_rest_api_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/08_roles_rest_api_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[9/11]${NC} Running test_roles.py (basic role tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_roles.py -v --tb=short \
    > "${OUTPUT_DIR}/09_roles_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/09_roles_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[10/11]${NC} Running test_oauth_real_user.py (OAuth real user tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_oauth_real_user.py -v --tb=short \
    > "${OUTPUT_DIR}/10_oauth_real_user_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/10_oauth_real_user_${TIMESTAMP}.txt"
echo ""

echo -e "${YELLOW}[11/11]${NC} Running test_base_model.py (base model tests)..."
docker compose -f docker/docker-compose.yaml exec -T runtime \
    pytest /app/integration_tests/test_base_model.py -v --tb=short \
    > "${OUTPUT_DIR}/11_base_model_${TIMESTAMP}.txt" 2>&1 || true
echo -e "${GREEN}✓${NC} Output saved to ${OUTPUT_DIR}/11_base_model_${TIMESTAMP}.txt"
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""

# Generate summary by checking each output file
echo "Test Results:"
echo ""

for file in "${OUTPUT_DIR}"/*_${TIMESTAMP}.txt; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        
        # Extract test counts from pytest output (macOS compatible)
        if grep -q "passed" "$file"; then
            # Get the summary line from pytest output
            summary=$(grep -E "[0-9]+ passed" "$file" | tail -1)
            
            if echo "$summary" | grep -q "failed"; then
                echo -e "${RED}✗${NC} $filename: $summary"
            elif echo "$summary" | grep -q "error"; then
                echo -e "${RED}✗${NC} $filename: $summary"
            else
                echo -e "${GREEN}✓${NC} $filename: $summary"
            fi
        else
            echo -e "${RED}✗${NC} $filename: No test results found"
        fi
    fi
done

echo ""
echo "=========================================="
echo -e "${GREEN}All test outputs saved to: ${OUTPUT_DIR}/${NC}"
echo "=========================================="
echo ""
echo "To view individual results:"
echo "  cat ${OUTPUT_DIR}/01_tests_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/02_oauth_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/03_roles_integration_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/04_auto_ui_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/05_chrome_ui_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/06_auth_comprehensive_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/07_model_utils_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/08_roles_rest_api_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/09_roles_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/10_oauth_real_user_${TIMESTAMP}.txt"
echo "  cat ${OUTPUT_DIR}/11_base_model_${TIMESTAMP}.txt"
echo ""


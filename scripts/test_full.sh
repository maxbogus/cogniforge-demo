#!/bin/bash
# CogniForge Full System Test Suite
# Usage: ./scripts/test_full.sh

set -e

BASE_URL="${BASE_URL:-http://localhost:3000}"
FAILED=0

echo "=========================================="
echo "CogniForge Full System Test Suite"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    FAILED=$((FAILED + 1))
}

section() {
    echo ""
    echo -e "${YELLOW}━━━ $1 ━━━${NC}"
}

# ============================================
# SECTION 1: Docker Status
# ============================================
section "1. Docker Services Status"

if docker compose ps | grep -q "Up"; then
    pass "Docker containers are running"
    docker compose ps
else
    fail "Docker containers are not running"
fi

# ============================================
# SECTION 2: Health Checks
# ============================================
section "2. Health Endpoints"

echo "Testing: GET /health"
if curl -sf "$BASE_URL/health" | grep -q "healthy"; then
    pass "GET /health"
else
    fail "GET /health"
fi

echo "Testing: GET /api/health"
if curl -sf "$BASE_URL/api/health" | grep -q "healthy"; then
    pass "GET /api/health"
else
    fail "GET /api/health"
fi

# ============================================
# SECTION 3: API Endpoints
# ============================================
section "3. API Endpoints"

echo "Testing: GET /"
if curl -sf "$BASE_URL/" | grep -q "CogniForge"; then
    pass "GET /"
else
    fail "GET /"
fi

echo "Testing: GET /api/version"
if curl -sf "$BASE_URL/api/version" | grep -q "api_version"; then
    pass "GET /api/version"
    curl -s "$BASE_URL/api/version" | head -1
else
    fail "GET /api/version"
fi

echo "Testing: GET /api/system/info"
if curl -sf "$BASE_URL/api/system/info" | grep -q "CogniForge"; then
    pass "GET /api/system/info"
else
    fail "GET /api/system/info"
fi

# ============================================
# SECTION 4: Documents API (if implemented)
# ============================================
section "4. Documents API"

echo "Testing: GET /api/documents"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/documents")
if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "404" ]; then
    pass "GET /api/documents (status: $RESPONSE)"
else
    fail "GET /api/documents (status: $RESPONSE)"
fi

# ============================================
# SECTION 5: Search API (if implemented)
# ============================================
section "5. Search API"

echo "Testing: POST /api/search"
SEARCH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "semantic search test"}' \
    -w "%{http_code}" -o /tmp/search_result.json)
if [ "$SEARCH_RESPONSE" = "200" ] || [ "$SEARCH_RESPONSE" = "404" ]; then
    pass "POST /api/search (status: $SEARCH_RESPONSE)"
else
    fail "POST /api/search (status: $SEARCH_RESPONSE)"
fi

# ============================================
# SECTION 6: Frontend
# ============================================
section "6. Frontend"

echo "Testing: GET / (Frontend)"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/")
if [ "$RESPONSE" = "200" ]; then
    pass "Frontend is accessible"
else
    fail "Frontend not accessible (status: $RESPONSE)"
fi

# ============================================
# SECTION 7: API Documentation
# ============================================
section "7. API Documentation"

echo "Testing: GET /api/docs"
RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/docs")
if [ "$RESPONSE" = "200" ]; then
    pass "Swagger docs accessible"
else
    fail "Swagger docs not accessible (status: $RESPONSE)"
fi

# ============================================
# SECTION 8: Data Directories
# ============================================
section "8. Data Directories"

for dir in data/inbound data/processed data/indices; do
    if [ -d "$dir" ]; then
        pass "Directory exists: $dir"
        FILE_COUNT=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "   Files in $dir: $FILE_COUNT"
    else
        fail "Directory missing: $dir"
    fi
done

# ============================================
# SUMMARY
# ============================================
section "SUMMARY"
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}💥 $FAILED TEST(S) FAILED${NC}"
    exit 1
fi

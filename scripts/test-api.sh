#!/bin/bash
# Тестирование API endpoints

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

BASE_URL="http://localhost:8000"

echo -e "${BLUE}=== Тестирование API ===${NC}\n"

# Test 1: Health check
echo -e "${YELLOW}1. Health Check...${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" $BASE_URL/health)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n1)

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Health check OK${NC}"
    echo "   Response: $BODY"
else
    echo -e "${RED}✗ Health check failed (HTTP $HTTP_CODE)${NC}"
    exit 1
fi

# Test 2: Waterbodies list
echo -e "\n${YELLOW}2. Waterbodies List...${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" $BASE_URL/api/waterbodies)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 200 ]; then
    COUNT=$(echo "$RESPONSE" | head -n1 | jq length 2>/dev/null || echo "0")
    echo -e "${GREEN}✓ Waterbodies endpoint OK (${COUNT} водоёмов)${NC}"

    if [ "$COUNT" -gt 0 ]; then
        FIRST_NAME=$(echo "$RESPONSE" | head -n1 | jq -r '.[0].name' 2>/dev/null)
        echo "   Первый водоём: $FIRST_NAME"
    fi
else
    echo -e "${RED}✗ Waterbodies endpoint failed (HTTP $HTTP_CODE)${NC}"
fi

# Test 3: Forecast (for first waterbody)
if [ "$COUNT" -gt 0 ]; then
    echo -e "\n${YELLOW}3. Forecast API...${NC}"
    LAT=$(echo "$RESPONSE" | head -n1 | jq -r '.[0].lat' 2>/dev/null)
    LON=$(echo "$RESPONSE" | head -n1 | jq -r '.[0].lon' 2>/dev/null)

    FORECAST=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/forecast?lat=$LAT&lon=$LON&hours=24&provider=open-meteo")
    HTTP_CODE=$(echo "$FORECAST" | tail -n1)

    if [ "$HTTP_CODE" -eq 200 ]; then
        HOURS=$(echo "$FORECAST" | head -n1 | jq '.hourly | length' 2>/dev/null || echo "0")
        echo -e "${GREEN}✓ Forecast endpoint OK (${HOURS} часов)${NC}"
        echo "   Координаты: $LAT, $LON"
    else
        echo -e "${RED}✗ Forecast endpoint failed (HTTP $HTTP_CODE)${NC}"
    fi

    # Test 4: Signals API
    echo -e "\n${YELLOW}4. Signals API...${NC}"
    SIGNALS=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/signals?lat=$LAT&lon=$LON&hours=24")
    HTTP_CODE=$(echo "$SIGNALS" | tail -n1)

    if [ "$HTTP_CODE" -eq 200 ]; then
        FLAGS=$(echo "$SIGNALS" | head -n1 | jq '.flags | length' 2>/dev/null || echo "0")
        echo -e "${GREEN}✓ Signals endpoint OK (${FLAGS} флагов)${NC}"
    else
        echo -e "${RED}✗ Signals endpoint failed (HTTP $HTTP_CODE)${NC}"
    fi

    # Test 5: Bite Index API
    echo -e "\n${YELLOW}5. Bite Index API...${NC}"
    BITE=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/bite-index?lat=$LAT&lon=$LON&hours=24&species=pike&species=perch")
    HTTP_CODE=$(echo "$BITE" | tail -n1)

    if [ "$HTTP_CODE" -eq 200 ]; then
        CONFIDENCE=$(echo "$BITE" | head -n1 | jq -r '.confidence' 2>/dev/null)
        AVG_SCORE=$(echo "$BITE" | head -n1 | jq '[.hourly[].score] | add / length | floor' 2>/dev/null || echo "N/A")
        echo -e "${GREEN}✓ Bite Index endpoint OK${NC}"
        echo "   Точность: $CONFIDENCE"
        echo "   Средний индекс: $AVG_SCORE/100"
    else
        echo -e "${RED}✗ Bite Index endpoint failed (HTTP $HTTP_CODE)${NC}"
    fi
fi

echo -e "\n${GREEN}=== Тестирование завершено ===${NC}"

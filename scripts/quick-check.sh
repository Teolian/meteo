#!/bin/bash
# Быстрая проверка работоспособности приложения

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Быстрая проверка Ice Fishing App ===${NC}\n"

# Проверка .env
echo -e "${YELLOW}Проверка конфигурации...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}✗ Файл .env не найден!${NC}"
    echo -e "${YELLOW}Запустите: make setup${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Файл .env найден${NC}"

# Проверка Docker
echo -e "\n${YELLOW}Проверка Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker не установлен${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker установлен${NC}"

# Проверка backend
echo -e "\n${YELLOW}Проверка backend...${NC}"
if docker ps | grep -q meteo-api; then
    echo -e "${GREEN}✓ Backend контейнер запущен${NC}"

    # Проверка health endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend API отвечает${NC}"

        # Проверка waterbodies
        WB_COUNT=$(curl -s http://localhost:8000/api/waterbodies | jq length 2>/dev/null || echo "0")
        if [ "$WB_COUNT" -gt 0 ]; then
            echo -e "${GREEN}✓ База данных заполнена ($WB_COUNT водоёмов)${NC}"
        else
            echo -e "${YELLOW}⚠ База данных пуста. Запустите: make seed${NC}"
        fi
    else
        echo -e "${RED}✗ Backend API не отвечает${NC}"
    fi
else
    echo -e "${RED}✗ Backend контейнер не запущен${NC}"
    echo -e "${YELLOW}Запустите: make start-docker${NC}"
fi

# Проверка frontend
echo -e "\n${YELLOW}Проверка frontend...${NC}"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend dev сервер запущен${NC}"
else
    echo -e "${YELLOW}⚠ Frontend dev сервер не запущен${NC}"
    echo -e "${YELLOW}Запустите: make start-frontend${NC}"
fi

# Проверка портов
echo -e "\n${YELLOW}Проверка портов...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Порт 8000 (backend) слушается${NC}"
else
    echo -e "${YELLOW}⚠ Порт 8000 свободен${NC}"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Порт 5173 (frontend) слушается${NC}"
else
    echo -e "${YELLOW}⚠ Порт 5173 свободен${NC}"
fi

# Итог
echo -e "\n${BLUE}=== Итоговая информация ===${NC}"
echo -e "Backend API:       http://localhost:8000"
echo -e "API Documentation: http://localhost:8000/docs"
echo -e "Frontend:          http://localhost:5173"
echo -e "\n${GREEN}Проверка завершена!${NC}"

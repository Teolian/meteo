#!/bin/bash
# Бэкап базы данных и конфигурации

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}=== Создание бэкапа ===${NC}\n"

# Создать директорию для бэкапов
mkdir -p "$BACKUP_DIR"

# Бэкап БД
if [ -f backend/data/meteo.db ]; then
    echo -e "${YELLOW}Копирование базы данных...${NC}"
    cp backend/data/meteo.db "$BACKUP_DIR/meteo.db"
    echo -e "${GREEN}✓ БД скопирована${NC}"
else
    echo -e "${YELLOW}⚠ База данных не найдена${NC}"
fi

# Бэкап .env
if [ -f .env ]; then
    echo -e "${YELLOW}Копирование конфигурации...${NC}"
    cp .env "$BACKUP_DIR/.env"
    echo -e "${GREEN}✓ Конфигурация скопирована${NC}"
else
    echo -e "${YELLOW}⚠ Файл .env не найден${NC}"
fi

# Создать архив
echo -e "${YELLOW}Создание архива...${NC}"
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR/.." "$(basename "$BACKUP_DIR")"
rm -rf "$BACKUP_DIR"

echo -e "${GREEN}✓ Бэкап создан: $BACKUP_DIR.tar.gz${NC}"

# Показать информацию
SIZE=$(du -h "$BACKUP_DIR.tar.gz" | cut -f1)
echo -e "\n${BLUE}Информация о бэкапе:${NC}"
echo -e "Файл:   $BACKUP_DIR.tar.gz"
echo -e "Размер: $SIZE"

# Очистить старые бэкапы (старше 30 дней)
echo -e "\n${YELLOW}Очистка старых бэкапов...${NC}"
find backups -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
echo -e "${GREEN}✓ Готово${NC}"

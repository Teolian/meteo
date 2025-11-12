# 📝 Шпаргалка по командам

Быстрая справка по самым полезным командам для работы с проектом.

## 🚀 Быстрый старт (3 команды)

```bash
make setup                    # Настройка проекта
nano .env                     # Отредактировать конфиг
make start && make seed       # Запуск + заполнение БД
```

## 📦 Основные команды

| Команда | Описание |
|---------|----------|
| `make help` | Показать все доступные команды |
| `make start` | Запустить весь стек |
| `make stop` | Остановить всё |
| `make restart` | Перезапустить |
| `make status` | Показать статус сервисов |
| `make logs` | Показать логи backend |

## 🗄️ База данных

| Команда | Описание |
|---------|----------|
| `make seed` | Заполнить БД начальными данными |
| `make seed-force` | Пересоздать БД и заполнить |
| `make db-shell` | Открыть SQLite shell |

## 🧪 Тестирование

| Команда | Описание |
|---------|----------|
| `make test` | Запустить все тесты |
| `make test-backend-cov` | Тесты с coverage отчётом |
| `make check` | Проверить статус сервисов |
| `./scripts/test-api.sh` | Протестировать все API endpoints |
| `./scripts/quick-check.sh` | Быстрая проверка работоспособности |

## 🏗️ Сборка

| Команда | Описание |
|---------|----------|
| `make build` | Собрать backend и frontend |
| `make build-frontend` | Собрать только frontend |
| `make preview-frontend` | Предпросмотр production сборки |

## 🧹 Очистка

| Команда | Описание |
|---------|----------|
| `make clean` | Очистить кеш |
| `make clean-cache` | Очистить только кеш |
| `make clean-data` | Удалить БД (с подтверждением) |
| `make clean-docker` | Удалить Docker контейнеры |
| `make clean-all` | Полная очистка проекта |

## 🔧 Разработка

| Команда | Описание |
|---------|----------|
| `make dev` | Режим разработки (hot reload) |
| `make shell-backend` | Открыть shell в контейнере |
| `make format-backend` | Форматировать код (black, isort) |
| `make lint-frontend` | Проверить frontend код |

## 📊 Скрипты

| Скрипт | Описание |
|--------|----------|
| `./scripts/quick-check.sh` | Быстрая проверка всех сервисов |
| `./scripts/test-api.sh` | Автотесты API endpoints |
| `./scripts/backup-data.sh` | Бэкап БД и конфигурации |

## 🌐 URLs

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

## 💡 Полезные комбинации

### Полная перезагрузка
```bash
make stop && make clean && make start && make seed
```

### Пересоздание БД
```bash
make stop
rm -f backend/data/meteo.db
make start-docker
make seed
```

### Обновление зависимостей
```bash
cd backend && . venv/bin/activate && pip install -r requirements.txt --upgrade
cd frontend && npm update
```

### Просмотр последних логов
```bash
make logs-backend-tail
```

### Проверка перед коммитом
```bash
make test && make lint-frontend
```

## 🐛 Решение проблем

### Backend не стартует
```bash
make logs              # Смотрим логи
make stop              # Останавливаем
make build-backend     # Пересобираем
make start-docker      # Запускаем
```

### База данных сломалась
```bash
make clean-data        # Удаляем БД
make start-docker      # Запускаем backend
make seed             # Заполняем заново
```

### Порты заняты
```bash
# Найти процесс на порту 8000
lsof -i :8000

# Убить процесс
kill -9 <PID>
```

### Всё сломалось
```bash
make clean-all         # Удалить всё
make setup            # Переустановить
make start            # Запустить
make seed             # Заполнить БД
```

## 📖 Документация

- **Полная документация**: [README.md](README.md)
- **Быстрый старт**: [QUICKSTART.md](QUICKSTART.md)
- **Все команды**: `make help`

## 🎯 Типичные задачи

### Добавление нового водоёма
```bash
# Через API (с запущенным backend)
curl -X POST http://localhost:8000/api/waterbodies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Озеро",
    "lat": 56.0,
    "lon": 37.0,
    "region": "Московская область",
    "type": "lake"
  }'

# Или через DB shell
make db-shell
# sqlite> INSERT INTO waterbodies ...
```

### Просмотр данных в БД
```bash
make db-shell
# sqlite> SELECT * FROM waterbodies;
# sqlite> SELECT COUNT(*) FROM forecast_hourly;
```

### Проверка версий
```bash
docker --version
node --version
python3 --version
make --version
```

### Бэкап перед обновлением
```bash
./scripts/backup-data.sh
# Бэкап сохранится в backups/YYYYMMDD_HHMMSS.tar.gz
```

---

**Совет**: Начните с `make help` для списка всех команд!

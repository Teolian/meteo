# 🚀 Быстрый старт

Это краткое руководство по запуску **Ice Fishing Bite Index** за 5 минут.

## ⚡ Самый быстрый способ (3 команды)

```bash
# 1. Настройка
make setup

# 2. Отредактируйте .env (укажите ваш email для MET Norway)
nano .env

# 3. Запуск
make start && make seed
```

**Готово!** 🎉

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs

---

## 📋 Пошаговая инструкция

### Шаг 1: Проверка требований

Убедитесь, что установлены:
- ✅ Docker
- ✅ Node.js 18+
- ✅ Make

```bash
docker --version
node --version
make --version
```

### Шаг 2: Настройка проекта

```bash
make setup
```

Эта команда:
- Создаст `.env` файл из `.env.example`
- Установит backend зависимости (Python venv)
- Установит frontend зависимости (npm)

### Шаг 3: Настройка `.env`

Откройте `.env` и настройте обязательные параметры:

```bash
nano .env
```

**Обязательно измените:**
```env
METNO_USER_AGENT=YourApp/0.1 (contact: your-email@example.com)
```

Замените `your-email@example.com` на ваш реальный email.

**Опционально:**
```env
# Если хотите использовать OpenWeather
OPENWEATHER_KEY=your_openweather_api_key
ENABLE_OPENWEATHER=true
```

### Шаг 4: Запуск приложения

```bash
make start
```

Эта команда запустит:
- ✅ Backend в Docker (порт 8000)
- ✅ Frontend dev server (порт 5173)

Подождите ~30 секунд пока backend полностью запустится.

### Шаг 5: Заполнение базы данных

```bash
make seed
```

Эта команда добавит 7 водоёмов ЦФО в базу данных.

---

## ✅ Проверка работоспособности

```bash
make check
```

Или запустите автоматическую проверку:

```bash
./scripts/quick-check.sh
```

Или откройте в браузере:
- 🌐 Frontend: http://localhost:5173
- 📚 API Docs: http://localhost:8000/docs
- 💚 Health: http://localhost:8000/health

---

## 🎯 Полезные команды

### Просмотр логов
```bash
make logs
```

### Проверка статуса
```bash
make status
```

### Остановка
```bash
make stop
```

### Перезапуск
```bash
make restart
```

### Тестирование API
```bash
./scripts/test-api.sh
```

### Очистка и перезапуск
```bash
make clean
make start
```

---

## 🐛 Решение проблем

### Backend не запускается

```bash
# Проверить логи
make logs

# Пересобрать контейнер
make stop
make build-backend
make start-docker
```

### Frontend не работает

```bash
# Переустановить зависимости
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### База данных пустая

```bash
# Пересоздать БД
make seed-force
```

### Порты заняты

Проверьте, что порты 8000 и 5173 свободны:

```bash
# Проверить порт 8000
lsof -i :8000

# Проверить порт 5173
lsof -i :5173
```

Если заняты - остановите процессы или измените порты в конфигурации.

---

## 📖 Дополнительная информация

### Все команды Makefile

```bash
make help
```

### Документация API

После запуска откройте:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Полная документация

См. [README.md](README.md) для подробной документации.

---

## 🎣 Первое использование

1. **Откройте приложение**: http://localhost:5173
2. **Выберите водоём** из списка (например, "Иваньковское водохранилище")
3. **Изучите прогноз**:
   - Текущая погода
   - Индекс клёва (0-100)
   - Графики давления, ветра, температуры
   - Сигналы фронтов
4. **Проверьте карту** - нажмите "Показать карту" для интерактивной карты

---

## ⏱️ Время запуска

- **Первая установка**: ~5-10 минут (загрузка зависимостей)
- **Последующие запуски**: ~30 секунд

---

## 💡 Советы

1. **Используйте `make dev`** для разработки с hot reload
2. **Проверяйте статус**: `make status` покажет состояние всех сервисов
3. **Бэкапьте данные**: `./scripts/backup-data.sh` перед крупными изменениями
4. **Тестируйте API**: `./scripts/test-api.sh` для быстрой проверки

---

**Вопросы?** См. [README.md](README.md) или создайте issue на GitHub.

Приятной рыбалки! 🎣❄️

.PHONY: help install install-backend install-frontend \
	start start-backend start-frontend start-docker \
	stop stop-docker \
	restart restart-docker \
	seed test test-backend lint-frontend \
	logs logs-backend logs-frontend \
	clean clean-cache clean-data clean-docker \
	build build-backend build-frontend \
	dev status check

# Цвета для вывода
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Переменные
BACKEND_DIR := backend
FRONTEND_DIR := frontend
DOCKER_COMPOSE := docker-compose
DOCKER_CONTAINER := meteo-api

##@ Основные команды

help: ## Показать эту справку
	@echo "$(BLUE)Ice Fishing Bite Index - Makefile команды$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Использование:\n  make $(GREEN)<команда>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Установка и настройка

install: install-backend install-frontend ## Установить все зависимости
	@echo "$(GREEN)✓ Все зависимости установлены$(NC)"

install-backend: ## Установить зависимости backend
	@echo "$(YELLOW)Установка backend зависимостей...$(NC)"
	@cd $(BACKEND_DIR) && \
		python3 -m venv venv && \
		. venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend зависимости установлены$(NC)"

install-frontend: ## Установить зависимости frontend
	@echo "$(YELLOW)Установка frontend зависимостей...$(NC)"
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)✓ Frontend зависимости установлены$(NC)"

setup: ## Первичная настройка проекта (создать .env, установить зависимости)
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Создание .env из .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ Файл .env создан. Отредактируйте его перед запуском!$(NC)"; \
	else \
		echo "$(GREEN)✓ Файл .env уже существует$(NC)"; \
	fi
	@make install
	@echo "$(GREEN)✓ Проект настроен! Отредактируйте .env и запустите 'make start'$(NC)"

##@ Запуск и остановка

start: start-docker start-frontend ## Запустить весь стек (docker backend + frontend dev)
	@echo "$(GREEN)✓ Приложение запущено!$(NC)"
	@echo "$(BLUE)Backend:$(NC)  http://localhost:8000"
	@echo "$(BLUE)API Docs:$(NC) http://localhost:8000/docs"
	@echo "$(BLUE)Frontend:$(NC) http://localhost:5173"

start-docker: ## Запустить backend в Docker
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ Файл .env не найден! Запустите 'make setup'$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Запуск backend в Docker...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Backend запущен в Docker$(NC)"
	@sleep 3
	@make check-backend

start-backend: ## Запустить backend локально (без Docker)
	@echo "$(YELLOW)Запуск backend локально...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate && \
		python -m app.main

start-frontend: ## Запустить frontend dev сервер
	@echo "$(YELLOW)Запуск frontend dev сервера...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

stop: stop-docker ## Остановить все сервисы
	@echo "$(GREEN)✓ Все сервисы остановлены$(NC)"

stop-docker: ## Остановить Docker контейнеры
	@echo "$(YELLOW)Остановка Docker контейнеров...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Docker контейнеры остановлены$(NC)"

restart: stop start ## Перезапустить все сервисы

restart-docker: ## Перезапустить Docker контейнеры
	@echo "$(YELLOW)Перезапуск Docker контейнеров...$(NC)"
	@$(DOCKER_COMPOSE) restart
	@echo "$(GREEN)✓ Docker контейнеры перезапущены$(NC)"

##@ База данных

seed: ## Заполнить БД начальными данными (водоёмы)
	@echo "$(YELLOW)Заполнение БД начальными данными...$(NC)"
	@if docker ps | grep -q $(DOCKER_CONTAINER); then \
		docker exec $(DOCKER_CONTAINER) python seed_db.py; \
	else \
		cd $(BACKEND_DIR) && . venv/bin/activate && python seed_db.py; \
	fi
	@echo "$(GREEN)✓ БД заполнена начальными данными$(NC)"

seed-force: ## Пересоздать БД и заполнить данными
	@echo "$(YELLOW)Удаление БД и пересоздание...$(NC)"
	@rm -f $(BACKEND_DIR)/data/meteo.db
	@make seed
	@echo "$(GREEN)✓ БД пересоздана$(NC)"

db-shell: ## Открыть SQLite shell для БД
	@if docker ps | grep -q $(DOCKER_CONTAINER); then \
		docker exec -it $(DOCKER_CONTAINER) sqlite3 /app/data/meteo.db; \
	else \
		sqlite3 $(BACKEND_DIR)/data/meteo.db; \
	fi

##@ Тестирование и проверки

test: test-backend ## Запустить все тесты
	@echo "$(GREEN)✓ Все тесты пройдены$(NC)"

test-backend: ## Запустить backend тесты
	@echo "$(YELLOW)Запуск backend тестов...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate && \
		pytest -v
	@echo "$(GREEN)✓ Backend тесты пройдены$(NC)"

test-backend-cov: ## Запустить backend тесты с coverage
	@echo "$(YELLOW)Запуск backend тестов с coverage...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate && \
		pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage отчёт: $(BACKEND_DIR)/htmlcov/index.html$(NC)"

lint-frontend: ## Проверить frontend код (ESLint)
	@echo "$(YELLOW)Проверка frontend кода...$(NC)"
	@cd $(FRONTEND_DIR) && npm run lint
	@echo "$(GREEN)✓ Frontend код проверен$(NC)"

check: check-backend check-frontend ## Проверить статус всех сервисов

check-backend: ## Проверить статус backend
	@echo "$(YELLOW)Проверка backend...$(NC)"
	@if docker ps | grep -q $(DOCKER_CONTAINER); then \
		echo "$(GREEN)✓ Backend Docker контейнер запущен$(NC)"; \
		curl -s http://localhost:8000/health > /dev/null && \
		echo "$(GREEN)✓ Backend API отвечает$(NC)" || \
		echo "$(RED)✗ Backend API не отвечает$(NC)"; \
	else \
		echo "$(RED)✗ Backend Docker контейнер не запущен$(NC)"; \
	fi

check-frontend: ## Проверить статус frontend
	@echo "$(YELLOW)Проверка frontend...$(NC)"
	@curl -s http://localhost:5173 > /dev/null && \
		echo "$(GREEN)✓ Frontend dev сервер отвечает$(NC)" || \
		echo "$(RED)✗ Frontend dev сервер не отвечает (запустите 'make start-frontend')$(NC)"

status: ## Показать статус всех сервисов
	@echo "$(BLUE)=== Статус сервисов ===$(NC)"
	@echo ""
	@make check
	@echo ""
	@echo "$(BLUE)=== Docker контейнеры ===$(NC)"
	@$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(BLUE)=== Процессы ===$(NC)"
	@ps aux | grep -E "(uvicorn|vite)" | grep -v grep || echo "Нет запущенных процессов"

##@ Логи

logs: logs-backend ## Показать логи всех сервисов

logs-backend: ## Показать логи backend (Docker)
	@$(DOCKER_COMPOSE) logs -f api

logs-backend-tail: ## Показать последние 100 строк логов backend
	@$(DOCKER_COMPOSE) logs --tail=100 api

logs-frontend: ## Frontend логи (в консоли dev сервера)
	@echo "$(YELLOW)Frontend логи доступны в терминале где запущен 'npm run dev'$(NC)"

##@ Сборка

build: build-backend build-frontend ## Собрать backend и frontend

build-backend: ## Собрать backend Docker образ
	@echo "$(YELLOW)Сборка backend Docker образа...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Backend Docker образ собран$(NC)"

build-frontend: ## Собрать frontend для production
	@echo "$(YELLOW)Сборка frontend для production...$(NC)"
	@cd $(FRONTEND_DIR) && npm run build
	@echo "$(GREEN)✓ Frontend собран в $(FRONTEND_DIR)/dist$(NC)"

preview-frontend: build-frontend ## Предпросмотр production сборки frontend
	@echo "$(YELLOW)Запуск preview production сборки...$(NC)"
	@cd $(FRONTEND_DIR) && npm run preview

##@ Очистка

clean: clean-cache ## Очистить кеш и временные файлы
	@echo "$(GREEN)✓ Очистка завершена$(NC)"

clean-cache: ## Очистить кеш (backend)
	@echo "$(YELLOW)Очистка кеша...$(NC)"
	@rm -rf $(BACKEND_DIR)/data/cache/*
	@find $(BACKEND_DIR) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find $(BACKEND_DIR) -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Кеш очищен$(NC)"

clean-data: ## Удалить БД и все данные
	@echo "$(RED)⚠ Удаление всех данных...$(NC)"
	@read -p "Вы уверены? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf $(BACKEND_DIR)/data/*; \
		echo "$(GREEN)✓ Данные удалены$(NC)"; \
	else \
		echo "$(YELLOW)Отменено$(NC)"; \
	fi

clean-docker: ## Удалить Docker контейнеры и volumes
	@echo "$(YELLOW)Удаление Docker контейнеров и volumes...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@echo "$(GREEN)✓ Docker контейнеры и volumes удалены$(NC)"

clean-all: clean-docker clean-data clean-cache ## Полная очистка (Docker, данные, кеш)
	@echo "$(YELLOW)Удаление node_modules и venv...$(NC)"
	@rm -rf $(FRONTEND_DIR)/node_modules
	@rm -rf $(FRONTEND_DIR)/dist
	@rm -rf $(BACKEND_DIR)/venv
	@echo "$(GREEN)✓ Полная очистка завершена$(NC)"

##@ Разработка

dev: ## Режим разработки (backend + frontend с hot reload)
	@echo "$(BLUE)Запуск в режиме разработки...$(NC)"
	@make start-docker
	@echo "$(YELLOW)Запуск frontend dev сервера...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

shell-backend: ## Открыть shell в backend контейнере
	@docker exec -it $(DOCKER_CONTAINER) bash

shell-db: db-shell ## Alias для db-shell

format-backend: ## Форматировать backend код (black)
	@echo "$(YELLOW)Форматирование backend кода...$(NC)"
	@cd $(BACKEND_DIR) && \
		. venv/bin/activate && \
		pip install black isort && \
		black app/ && \
		isort app/
	@echo "$(GREEN)✓ Backend код отформатирован$(NC)"

##@ Информация

env-check: ## Проверить наличие необходимых переменных окружения
	@echo "$(BLUE)Проверка конфигурации...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)✗ Файл .env не найден!$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Файл .env найден$(NC)"
	@if grep -q "METNO_USER_AGENT=.*@" .env; then \
		echo "$(GREEN)✓ METNO_USER_AGENT настроен$(NC)"; \
	else \
		echo "$(YELLOW)⚠ METNO_USER_AGENT не настроен или некорректен$(NC)"; \
	fi
	@if grep -q "TZ=Europe/Moscow" .env; then \
		echo "$(GREEN)✓ Timezone настроена$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Timezone не настроена$(NC)"; \
	fi

info: ## Показать информацию о проекте
	@echo "$(BLUE)=== Ice Fishing Bite Index MVP ===$(NC)"
	@echo "Backend:  FastAPI + Python 3.11"
	@echo "Frontend: React 18 + Vite + TypeScript"
	@echo "Database: SQLite"
	@echo ""
	@echo "$(BLUE)Полезные команды:$(NC)"
	@echo "  make setup          - Первичная настройка"
	@echo "  make start          - Запустить все"
	@echo "  make dev            - Режим разработки"
	@echo "  make test           - Запустить тесты"
	@echo "  make logs           - Показать логи"
	@echo "  make status         - Статус сервисов"
	@echo "  make clean          - Очистить кеш"
	@echo ""
	@echo "$(BLUE)Документация:$(NC)"
	@echo "  README.md           - Полная документация"
	@echo "  http://localhost:8000/docs - API документация"

urls: ## Показать URLs всех сервисов
	@echo "$(BLUE)=== URLs сервисов ===$(NC)"
	@echo "Backend API:       http://localhost:8000"
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "API ReDoc:         http://localhost:8000/redoc"
	@echo "Frontend:          http://localhost:5173"
	@echo "Health Check:      http://localhost:8000/health"

# Detect Operating System
ifeq ($(OS),Windows_NT)
    SHELL := cmd.exe
    RM := del /Q /F
    PYTHON := .venv\Scripts\python
    PIP := .venv\Scripts\pip
    UV := uv
else
    SHELL := /bin/sh
    RM := rm -rf
    PYTHON := .venv/bin/python
    PIP := .venv/bin/pip
    UV := uv
endif
# Default user count for seeding
USERS ?= 10

.PHONY: help dev build down logs migrate seed shell test clean local-setup local-run local-seed

# Default target showing help
help:
	@echo "Rojgari Makefile (Cross-Platform Support)"
	@echo "==========================================="
	@echo "Docker-based Commands:"
	@echo "  make dev          - Run development environment in foreground"
	@echo "  make build        - Build or rebuild Docker containers"
	@echo "  make down         - Stop and remove Docker containers"
	@echo "  make logs         - Tail Docker logs"
	@echo "  make migrate      - Run Django migrations inside container"
	@echo "  make seed         - Seed PostgreSQL database inside container (pass USERS=N to customize)"
	@echo "  make shell        - Open a Django shell inside container"
	@echo "  make test         - Run Django test suite inside container"
	@echo ""
	@echo "Local Development Commands (using uv):"
	@echo "  make local-setup  - Setup virtualenv and install dependencies locally"
	@echo "  make local-run    - Run local Django server using SQLite fallback"
	@echo "  make local-seed   - Seed the local database (pass USERS=N to customize)"
	@echo "  make clean        - Clean pyc and cache files"

# --- Docker Services ---

dev:
	docker compose up -d

build:
	docker compose build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py migrate
	docker compose exec web python manage.py seed --users $(USERS)

shell:
	docker compose exec web python manage.py shell

test:
	docker compose exec web python manage.py test

# --- Local Host Machine (via uv) ---

local-setup:
	$(UV) sync
	@echo "Setup complete. Virtual environment ready."

local-run:
	$(UV) run python manage.py migrate
	$(UV) run python manage.py runserver 0.0.0.0:8000

local-seed:
	$(UV) run python manage.py migrate
	$(UV) run python manage.py seed --users $(USERS)

# --- Cleaning Utilities ---

clean:
	@echo "Cleaning cache files..."
ifeq ($(OS),Windows_NT)
	@for /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul || true
	@if exist db.sqlite3 del /f db.sqlite3 2>nul || true
else
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f db.sqlite3
endif
	@echo "Clean finished."

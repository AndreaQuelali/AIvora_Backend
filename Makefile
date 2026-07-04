.PHONY: help dev worker test lint format type-check pre-commit \
        migrate migrate-create docker-up docker-down docker-build \
        clean install install-dev

# Default target
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------
install: ## Install production dependencies
	pip install -e .

install-dev: ## Install all dependencies including dev
	pip install -e ".[dev]"
	pre-commit install

dev: ## Run development server with hot reload
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

worker: ## Run Celery worker
	celery -A app.workers.celery_worker:celery_app worker --loglevel=info -Q default,documents,notifications

worker-beat: ## Run Celery beat scheduler
	celery -A app.workers.celery_worker:celery_app beat --loglevel=info

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------
lint: ## Run ruff linter
	ruff check .

format: ## Run ruff formatter
	ruff format .

lint-fix: ## Run ruff linter and auto-fix
	ruff check . --fix
	ruff format .

type-check: ## Run mypy type checker
	mypy app/

pre-commit-run: ## Run pre-commit hooks on all files
	pre-commit run --all-files

quality: lint type-check ## Run all quality checks

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------
test: ## Run pytest
	pytest tests/ -v

test-unit: ## Run only unit tests
	pytest tests/unit/ -v -m unit

test-integration: ## Run only integration tests
	pytest tests/integration/ -v -m integration

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

# ---------------------------------------------------------------------------
# Database / Migrations
# ---------------------------------------------------------------------------
migrate: ## Run alembic migrations (upgrade to head)
	alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	alembic revision --autogenerate -m "$(MSG)"

migrate-down: ## Rollback last migration
	alembic downgrade -1

migrate-history: ## Show migration history
	alembic history --verbose

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------
docker-build: ## Build backend Docker image
	docker build -t aivora-backend:latest .

docker-up: ## Start all services via Docker Compose
	docker compose up -d

docker-down: ## Stop all services
	docker compose down

docker-logs: ## Follow logs from all services
	docker compose logs -f

docker-ps: ## Show running containers
	docker compose ps

docker-shell: ## Open shell in backend container
	docker compose exec backend bash

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
clean: ## Remove Python cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

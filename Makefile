.PHONY: help install run dev test lint docker-up docker-down clean setup

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ──────────────────────────────────────────────

setup: ## Full project setup (backend + frontend)
	@echo "🔧  Setting up backend..."
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt
	cd backend && python -m spacy download en_core_web_sm
	@echo "🔧  Setting up frontend..."
	cd frontend && npm ci
	@echo "✅  Setup complete!"

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm ci

# ─── Development ────────────────────────────────────────

run: ## Run backend and frontend concurrently
	@echo "Starting backend on :8000 and frontend on :3000..."
	@make run-backend & make run-frontend

run-backend: ## Run backend only
	cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

run-frontend: ## Run frontend only
	cd frontend && npm start

dev: run ## Alias for run

# ─── Testing ────────────────────────────────────────────

test: ## Run backend tests
	cd backend && python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html --tb=short
	@echo "📊  Coverage report: backend/htmlcov/index.html"

# ─── Linting ────────────────────────────────────────────

lint: ## Lint backend code
	cd backend && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	cd backend && flake8 . --count --exit-zero --max-complexity=15 --max-line-length=120 --statistics

lint-frontend: ## Lint frontend code
	cd frontend && npx eslint src/ --ext .js,.jsx

# ─── Docker ─────────────────────────────────────────────

docker-up: ## Start all services with Docker Compose
	docker compose up -d --build

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## Tail Docker logs
	docker compose logs -f

docker-clean: ## Stop services and remove volumes
	docker compose down -v --remove-orphans

# ─── Utilities ──────────────────────────────────────────

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/build
	@echo "🧹  Cleaned!"

build-frontend: ## Build frontend for production
	cd frontend && npm run build

collect: ## Trigger a one-time data collection
	cd backend && python -c "import asyncio; from app.services.collector import run_collection_once; asyncio.run(run_collection_once())"

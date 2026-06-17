.PHONY: help up down build logs shell-backend shell-frontend test migrate seed clean

# ── Colors ────────────────────────────────────────────────────────────────────
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RESET  := \033[0m

help: ## Show this help
	@echo ""
	@echo "$(GREEN)Double N Trading$(RESET) — Development Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# ── Docker lifecycle ──────────────────────────────────────────────────────────
up: ## Start all services (detached)
	@cp -n .env.example .env 2>/dev/null || true
	docker compose up -d --build
	@echo "$(GREEN)✓ Running at:$(RESET)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API docs: http://localhost:8000/api/docs"

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

build: ## Build images without starting
	docker compose build

logs: ## Tail logs (all services)
	docker compose logs -f

logs-backend: ## Tail backend logs only
	docker compose logs -f backend

logs-frontend: ## Tail frontend logs only
	docker compose logs -f frontend

# ── Database ──────────────────────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	docker compose exec backend alembic upgrade head

migrate-create: ## Create new migration (NAME=description)
	docker compose exec backend alembic revision --autogenerate -m "$(NAME)"

migrate-down: ## Rollback last migration
	docker compose exec backend alembic downgrade -1

db-shell: ## Open psql shell
	docker compose exec postgres psql -U postgres -d double_n_trading

# ── Shells ────────────────────────────────────────────────────────────────────
shell-backend: ## Open shell in backend container
	docker compose exec backend bash

shell-frontend: ## Open shell in frontend container
	docker compose exec frontend sh

# ── Testing ───────────────────────────────────────────────────────────────────
test: ## Run all backend tests
	docker compose exec backend pytest tests/ -v

test-unit: ## Run unit tests only
	docker compose exec backend pytest tests/unit/ -v

test-integration: ## Run integration tests only
	docker compose exec backend pytest tests/integration/ -v

test-cov: ## Run tests with coverage report
	docker compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

# ── Local dev (no Docker) ─────────────────────────────────────────────────────
dev-backend: ## Start backend dev server (requires local venv)
	cd backend && uvicorn app.main:app --reload --port 8000

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean: ## Remove containers, volumes, and images
	docker compose down -v --rmi local

clean-all: ## Full clean including DB data (DESTRUCTIVE)
	docker compose down -v --rmi all
	docker volume prune -f

# ── Health checks ─────────────────────────────────────────────────────────────
health: ## Check service health
	@echo "Backend:  $$(curl -sf http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo 'UNREACHABLE')"
	@echo "Frontend: $$(curl -sf -o /dev/null -w '%{http_code}' http://localhost:3000 || echo 'UNREACHABLE')"

# ── Secret generation ─────────────────────────────────────────────────────────
gen-secret: ## Generate a secure SECRET_KEY
	@python3 -c "import secrets; print(secrets.token_hex(64))"

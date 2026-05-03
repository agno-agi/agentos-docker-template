# AgentOS – local run commands
# Usage: make [target]

.PHONY: help install up down logs logs-api logs-db run run-dev db load-docs clean reset-db format lint

help:
	@echo "AgentOS – local commands"
	@echo ""
	@echo "  make install   Create venv and install deps (requires uv)"
	@echo "  make up        Start full stack with Docker (API + DB)"
	@echo "  make down     Stop Docker stack"
	@echo "  make logs      Follow API logs"
	@echo "  make logs-api  Follow API logs"
	@echo "  make logs-db   Follow DB logs"
	@echo "  make run       Start API locally (expects venv + DB; use 'make db' first)"
	@echo "  make run-dev   Start API with reload (RUNTIME_ENV=dev)"
	@echo "  make db        Start only Postgres (for local dev)"
	@echo "  make load-docs Load default docs into Knowledge Agent (run after 'make up')"
	@echo "  make clean     Stop stack and remove volumes"
	@echo "  make reset-db  Same as clean; use if DB auth fails after changing .env"
	@echo "  make format    Run formatter (scripts/format.sh)"
	@echo "  make lint     Run linter"

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
install:
	./scripts/venv_setup.sh
	@echo "Then: source .venv/bin/activate"

# -----------------------------------------------------------------------------
# Docker (full stack)
# -----------------------------------------------------------------------------
up:
	docker compose up -d --build

down:
	docker compose down

logs: logs-api

logs-api:
	docker compose logs -f agentos-api

logs-db:
	docker compose logs -f agentos-db

clean:
	docker compose down -v

# Reset DB only (drop volumes and recreate; use if auth fails after changing .env)
reset-db:
	docker compose down -v
	@echo "Volumes removed. Run 'make up' to start fresh (Postgres will init with current .env)."

# -----------------------------------------------------------------------------
# Local dev (venv + DB in Docker)
# -----------------------------------------------------------------------------
db:
	docker compose up -d agentos-db

run:
	python -m app.main

run-dev:
	RUNTIME_ENV=dev python -m app.main

# -----------------------------------------------------------------------------
# One-off / maintenance
# -----------------------------------------------------------------------------
load-docs:
	docker exec -it agentos-api python -m src.agents.knowledge_agent

format:
	@test -f scripts/format.sh && ./scripts/format.sh || true

lint:
	@command -v ruff >/dev/null 2>&1 && ruff check . || echo "Install ruff for linting"

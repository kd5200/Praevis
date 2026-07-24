.PHONY: setup up down dev api web worker test test-security lint typecheck migrate seed clean help

help:
	@echo "Praevis Make targets:"
	@echo "  setup          Install Python and Node dependencies"
	@echo "  up / down      Start/stop Postgres + Redis"
	@echo "  api / web / worker  Run application processes"
	@echo "  test / test-security / lint / typecheck"
	@echo "  migrate / seed / clean"

setup:
	python3 -m pip install -e ".[dev]"
	python3 -m pip install -e "./apps/api"
	python3 -m pip install -e "./apps/worker"
	python3 -m pip install -e "./packages/sdk-python"
	cd apps/web && npm install

up:
	docker compose up -d postgres redis

down:
	docker compose down

dev: up
	@echo "Infra up. Run make api / make web / make worker in separate terminals."

api:
	cd apps/api && python3 -m uvicorn praevis_api.main:app --host $${API_HOST:-0.0.0.0} --port $${API_PORT:-8000} --reload

web:
	cd apps/web && npm run dev

worker:
	cd apps/worker && python3 -m celery -A praevis_worker.celery_app:app worker --loglevel=$${LOG_LEVEL:-INFO}

test:
	python3 -m pytest -q

test-security:
	python3 -m pytest -q tests/security apps/api/tests -m security

lint:
	python3 -m ruff check .
	python3 -m ruff format --check .
	cd apps/web && npm run lint

typecheck:
	python3 -m mypy apps/api/src apps/worker/src packages/sdk-python/src
	cd apps/web && npm run typecheck

migrate:
	cd apps/api && DATABASE_URL=$${DATABASE_URL:-postgresql+psycopg://praevis:praevis@localhost:15432/praevis} python3 -m alembic upgrade head

seed:
	@echo "No seed data defined yet."

clean:
	find . -type d -name __pycache__ -not -path './.git/*' -prune -exec rm -rf {} +
	find . -type d -name .pytest_cache -prune -exec rm -rf {} +
	find . -type d -name .mypy_cache -prune -exec rm -rf {} +
	find . -type d -name .ruff_cache -prune -exec rm -rf {} +
	find . -type d -name .next -prune -exec rm -rf {} +
	find . -type d -name node_modules -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} + 2>/dev/null || true

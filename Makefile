.PHONY: install dev test test-integration lint format migrate upgrade

install:
	uv sync

dev:
	uv sync
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest

test-integration:
	uv run pytest -m integration

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run lint-imports

format:
	uv run ruff format .
	uv run ruff check --fix .

migrate:
	uv run alembic revision --autogenerate -m "$(m)"

upgrade:
	uv run alembic upgrade head

.PHONY: install dev api web test lint build verify clean-data

PYTHON := .venv/bin/python
UV := uv
PYTHON_INSTALL ?= python3.12

install:
	$(UV) venv --python $(PYTHON_INSTALL)
	$(UV) sync --extra dev
	cd frontend && npm ci

api:
	$(PYTHON) -m uvicorn app.main:app --app-dir backend --reload --port 8000

web:
	cd frontend && npm run dev

dev:
	@echo "Run 'make api' and 'make web' in separate terminals."

test:
	$(PYTHON) -m pytest
	cd frontend && npm test -- --run

lint:
	$(PYTHON) -m ruff check backend tests
	cd frontend && npm run lint

build:
	cd frontend && npm run build

verify: lint test build

clean-data:
	@echo "Data deletion is intentionally manual. Remove only the explicit data directory you intend to reset."

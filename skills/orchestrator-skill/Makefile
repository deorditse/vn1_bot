ROOT := ../..
SERVICE := orchestrator-skill
PORT ?= 8020

.PHONY: run run-prod test prod restart stop

run:
	uv sync
	PYTHONPATH=src:../../shared/python API_MODE=DEV API_PORT=$(PORT) uv run python src/app/run.py

run-prod:
	uv sync
	PYTHONPATH=src:../../shared/python API_MODE=PROD API_PORT=$(PORT) uv run python src/app/run.py

test:
	uv run ruff check src
	PYTHONPATH=src:../../shared/python python3 -m compileall -q src

prod:
	$(MAKE) -C $(ROOT) prod SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

stop:
	$(MAKE) -C $(ROOT) stop SERVICE=$(SERVICE)

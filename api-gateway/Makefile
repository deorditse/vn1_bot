ROOT := ..
SERVICE := api-gateway
PORT ?= 8000

.PHONY: run run-prod test prod restart stop

run:
	uv sync
	@set -a; if [ -f .env ]; then . ./.env; fi; set +a; \
	PYTHONPATH=src API_MODE=DEV API_PORT=$(PORT) uv run python src/app/run.py

run-prod:
	uv sync
	@set -a; if [ -f .env ]; then . ./.env; fi; set +a; \
	PYTHONPATH=src API_MODE=PROD API_PORT=$(PORT) uv run python src/app/run.py

test:
	uv run ruff check src
	python3 -m compileall -q src

prod:
	$(MAKE) -C $(ROOT) prod SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

stop:
	$(MAKE) -C $(ROOT) stop SERVICE=$(SERVICE)

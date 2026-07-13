ROOT := ..
SERVICE := backend-vn1
PORT ?= 8010
ENV_FILE ?= .env

.PHONY: run run-prod test prod restart stop

run:
	uv sync
	@set -a; if [ -f "$(ENV_FILE)" ]; then . ./$(ENV_FILE); fi; set +a; \
	PYTHONPATH=src:../shared/python \
	API_MODE=DEV \
	API_PORT=$(PORT) \
	AUTH_CONTEXT_URL=$${AUTH_CONTEXT_URL:-http://localhost:8030/v1/auth/context} \
	uv run python3 src/app/run.py

run-prod:
	uv sync
	@set -a; if [ -f "$(ENV_FILE)" ]; then . ./$(ENV_FILE); fi; set +a; \
	PYTHONPATH=src:../shared/python API_MODE=PROD API_PORT=$(PORT) uv run python3 src/app/run.py

test:
	uv run ruff check src
	PYTHONPATH=src:../shared/python python3 -m compileall -q src

prod:
	$(MAKE) -C $(ROOT) prod SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

stop:
	$(MAKE) -C $(ROOT) stop SERVICE=$(SERVICE)

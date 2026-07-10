ROOT := ..
SERVICE := api-gateway
PORT ?= 8000

.PHONY: init sync dev prod test logs restart down

init:
	@test -f .env || cp .env.example .env

sync:
	uv sync

dev: init sync
	@set -a; . ./.env; set +a; \
	PYTHONPATH=src API_MODE=DEV AUTH_ENABLED=false API_PORT=$(PORT) uv run python src/app/run.py

prod:
	$(MAKE) -C $(ROOT) up SERVICE=$(SERVICE)

test:
	python3 -m compileall -q src

logs:
	$(MAKE) -C $(ROOT) logs SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

down:
	$(MAKE) -C $(ROOT) down

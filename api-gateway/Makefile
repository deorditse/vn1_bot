ROOT := ..
SERVICE := api-gateway
PORT ?= 8000

.PHONY: run run-prod test prod restart stop

run:
	uv sync
	@set -a; if [ -f .env ]; then . ./.env; fi; set +a; \
	PYTHONPATH=src:../shared/python \
	API_MODE=DEV \
	API_PORT=$(PORT) \
	GENERATOR_BASE_URL=$${GENERATOR_BASE_URL:-http://localhost:8010} \
	AUTH_CONTEXT_URL=$${AUTH_CONTEXT_URL:-http://localhost:8030/v1/auth/context} \
	ORCHESTRATOR_SKILL_BASE_URL=$${ORCHESTRATOR_SKILL_BASE_URL:-http://localhost:8020} \
	GITLAB_SKILL_BASE_URL=$${GITLAB_SKILL_BASE_URL:-http://localhost:8022} \
	uv run python src/app/run.py

run-prod:
	uv sync
	@set -a; if [ -f .env ]; then . ./.env; fi; set +a; \
	PYTHONPATH=src:../shared/python API_MODE=PROD API_PORT=$(PORT) uv run python src/app/run.py

test:
	uv run ruff check src
	PYTHONPATH=src:../shared/python python3 -m compileall -q src

prod:
	$(MAKE) -C $(ROOT) prod SERVICE=$(SERVICE)

restart:
	$(MAKE) -C $(ROOT) restart SERVICE=$(SERVICE)

stop:
	$(MAKE) -C $(ROOT) stop SERVICE=$(SERVICE)

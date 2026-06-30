.PHONY: sync run run-dev run-prod stop frontend-install frontend-run frontend-build frontend-preview docker-up docker-build docker-down docker-logs docker-logs-backend docker-logs-frontend docker-logs-nginx docker-logs-keycloak

PORT ?= 8010
FRONTEND_PORT ?= 5173
ENV_FILE ?= .env
COMPOSE = docker compose -f docker-compose.yml

sync:
	uv sync

run:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then . "$(ENV_FILE)"; fi; \
	set +a; \
	API_MODE=DEV API_PORT=$(PORT) uv run python3 src/app/run.py

run-dev: run

run-prod:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then . "$(ENV_FILE)"; fi; \
	set +a; \
	API_MODE=PROD API_PORT=$(PORT) uv run python3 src/app/run.py

stop:
	@pids=$$(lsof -tiTCP:$(PORT) -sTCP:LISTEN); \
	if [ -n "$$pids" ]; then kill $$pids; fi
	@pids=$$(lsof -tiTCP:$(FRONTEND_PORT) -sTCP:LISTEN); \
	if [ -n "$$pids" ]; then kill $$pids; fi

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev -- --port $(FRONTEND_PORT)

frontend-build:
	cd frontend && npm run build

frontend-preview:
	cd frontend && npm run preview -- --port $(FRONTEND_PORT)

docker-up:
	$(COMPOSE) up -d

docker-build:
	$(COMPOSE) up -d --build

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f

docker-logs-backend:
	$(COMPOSE) logs -f backend-vn1

docker-logs-frontend:
	$(COMPOSE) logs -f frontend

docker-logs-nginx:
	$(COMPOSE) logs -f nginx

docker-logs-keycloak:
	$(COMPOSE) logs -f keycloak

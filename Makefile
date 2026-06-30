.PHONY: sync ensure-local-cert run run-dev run-prod run-with-local-cert run-local run-local-prod stop stop-local frontend-install frontend-run frontend-build frontend-preview docker-up docker-build docker-down docker-logs docker-logs-backend docker-logs-frontend docker-logs-nginx docker-logs-keycloak restart-backend check-proxy check-openai check-xray

PORT ?= 8010
FRONTEND_PORT ?= 5173
ENV_FILE ?= .env
DOCKER ?= docker
COMPOSE = $(DOCKER) compose -f docker-compose.yml
CERT_DOMAIN ?= ai-bot.vn1.ru

sync:
	uv sync

ensure-local-cert:
	@if [ ! -f "certbot/conf/live/$(CERT_DOMAIN)/fullchain.pem" ] || [ ! -f "certbot/conf/live/$(CERT_DOMAIN)/privkey.pem" ]; then \
		mkdir -p certbot/conf/live/$(CERT_DOMAIN); \
		openssl req -x509 -nodes -newkey rsa:2048 -days 365 \
			-keyout certbot/conf/live/$(CERT_DOMAIN)/privkey.pem \
			-out certbot/conf/live/$(CERT_DOMAIN)/fullchain.pem \
			-subj "/CN=$(CERT_DOMAIN)"; \
	fi

run:
	$(COMPOSE) up -d --build

run-prod: run

run-with-local-cert: ensure-local-cert
	$(COMPOSE) up -d --build

run-local:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then . "$(ENV_FILE)"; fi; \
	set +a; \
	API_MODE=DEV API_PORT=$(PORT) uv run python3 src/app/run.py

run-local-prod:
	@set -a; \
	if [ -f "$(ENV_FILE)" ]; then . "$(ENV_FILE)"; fi; \
	set +a; \
	API_MODE=PROD API_PORT=$(PORT) uv run python3 src/app/run.py

stop:
	$(COMPOSE) down

stop-local:
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

restart-backend:
	$(COMPOSE) up -d --build --force-recreate backend-vn1

check-proxy:
	$(COMPOSE) exec backend-vn1 uv run python -c 'import os; from common.env import proxy_url; print("proxy_url =", proxy_url()); print("PROXY =", os.getenv("PROXY")); print("ALL_PROXY =", os.getenv("ALL_PROXY")); print("HTTPS_PROXY =", os.getenv("HTTPS_PROXY")); print("HTTP_PROXY =", os.getenv("HTTP_PROXY")); print("NO_PROXY =", os.getenv("NO_PROXY"))'

check-openai:
	$(COMPOSE) exec backend-vn1 uv run python -c 'import os, httpx; proxy = os.getenv("PROXY") or os.getenv("ALL_PROXY") or os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY"); print("proxy =", proxy); response = httpx.get("https://api.openai.com/v1/models", headers={"Authorization": "Bearer " + os.getenv("OPENAI_API_KEY", "")}, proxy=proxy, timeout=30); print(response.status_code); print(response.text[:300])'

check-xray:
	$(COMPOSE) exec backend-vn1 uv run python -c 'import socket; sock = socket.create_connection(("xray", 10808), timeout=5); print("xray:10808 ok"); sock.close()'

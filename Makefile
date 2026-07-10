SHELL := /bin/sh

DOCKER ?= docker
SERVICE ?=
REPO_ROOT := $(CURDIR)

COMPOSE_FILES = \
	-f docker-compose.yml \
	-f shared/docker-compose.yaml \
	-f auth/docker-compose.yaml \
	-f frontend/docker-compose.yaml \
	-f generator/docker-compose.yaml \
	-f skills/docker-compose.yaml \
	-f api-gateway/docker-compose.yaml

COMPOSE = REPO_ROOT=$(REPO_ROOT) $(DOCKER) compose $(COMPOSE_FILES)

.PHONY: run run-prod test prod restart stop

run: prod

run-prod: prod

test:
	$(COMPOSE) config >/dev/null

prod:
	$(COMPOSE) up -d --build $(SERVICE)

restart:
	$(COMPOSE) up -d --build --force-recreate $(SERVICE)

stop:
	@if [ -n "$(SERVICE)" ]; then \
		$(COMPOSE) stop $(SERVICE); \
	else \
		$(COMPOSE) down; \
	fi

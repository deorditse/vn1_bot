# Repository Guidelines

## Project Structure & Module Organization

This repository contains the VN1 auth service. Application code lives under `src/`.

- `src/app/` contains the FastAPI entrypoint, API setup, routers, schemas, and error handling.
- `src/common/` contains shared service utilities, exceptions, and Dynaconf settings.
- `src/common/config/settings/` contains default, dev, and prod TOML settings selected by `API_MODE`.
- `src/infrastructure/keycloak/` contains the current Keycloak auth provider, its README, example env file, and realm export.
- Root files such as `Dockerfile`, `docker-compose.yaml`, `Makefile`, `pyproject.toml`, and `.env.example` define runtime, dependency, and local development behavior.

No dedicated `tests/` directory is currently committed. Add one when introducing automated tests.

## Build, Test, and Development Commands

- `uv sync` installs the project dependencies from `pyproject.toml` and `uv.lock`.
- `make run` starts the service locally in dev mode with `PYTHONPATH=src`, `API_MODE=DEV`, and default `PORT=8030`.
- `make run-prod` starts the service with `API_MODE=PROD`.
- `make test` runs `ruff check src` and compiles all Python files with `compileall`.
- `make prod`, `make restart`, and `make stop` delegate service orchestration to the parent repository.

Use `PORT=8040 make run` to override the local port.

## Coding Style & Naming Conventions

The service targets Python 3.13. Follow normal Python naming: modules and functions in `snake_case`, classes in `PascalCase`, constants in `UPPER_SNAKE_CASE`.

Keep imports inside this service. Ruff bans cross-service imports such as `api_gateway`, `generator`, `skills`, and imports through the monorepo root `vn1_bot`; communicate with other services over HTTP instead.

Keep code under `src/`, prefer explicit FastAPI schemas in `src/app/api/schemas/`, and keep provider-specific behavior inside `src/infrastructure/`.

## Testing Guidelines

Current verification is `make test`. When adding tests, place them in a root-level `tests/` directory and name files `test_*.py`. Prefer focused API/router tests for request behavior and provider tests for Keycloak integration boundaries. Keep tests independent of real secrets; use `.env.example` and test overrides.

## Commit & Pull Request Guidelines

Recent commit messages are short, lowercase summaries such as `review`, `architecture`, `infra`, and `frontend`. Keep commits concise and scoped to one change.

Pull requests should include a brief description, validation steps such as `make test`, related issue links when available, and screenshots or request/response examples for API-visible behavior changes.

## Security & Configuration Tips

Do not commit real `.env` files, client secrets, tokens, or production Keycloak credentials. Add new configuration defaults to `settings.toml`, mode-specific overrides to `settings.dev.toml` or `settings.prod.toml`, and document required secret values in `.env.example`.

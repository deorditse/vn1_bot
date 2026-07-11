# Repository Guidelines

## Project Structure & Module Organization

This repository contains the `generator` Python backend service. Runtime code lives in `src/` and is organized by responsibility: `src/app/` contains FastAPI entrypoints, routers, schemas, use cases, and prompts; `src/domain/` contains domain services and auth helpers; `src/infrastructure/` contains LLM, converter, and observability integrations; `src/common/` contains shared settings, logging, errors, and utilities. Configuration defaults are in `src/common/config/settings/`. Documentation, notebooks, and sample inputs live in `docs/`. Container and local orchestration files are `Dockerfile`, `docker-compose.yaml`, and `Makefile`.

## Build, Test, and Development Commands

- `uv sync`: install dependencies from `pyproject.toml` and `uv.lock`.
- `make run`: run the service locally with `API_MODE=DEV` on port `8010` unless `PORT` is set.
- `make run-prod`: run locally with `API_MODE=PROD`.
- `make test`: run `ruff check src` and compile all Python modules.
- `make prod`, `make restart`, `make stop`: delegate service operations to the parent repository Makefile.

Use Python `3.13`, as specified by `.python-version` and `pyproject.toml`.

## Coding Style & Naming Conventions

Keep source under `src/` and use package imports relative to this service. Ruff is configured in `pyproject.toml`; run `uv run ruff check src` before submitting changes. The active lint rule bans cross-service imports such as `api_gateway`, `skills`, `generator`, and `vn1_bot`; call external services over HTTP/SSE instead. Follow standard Python naming: `snake_case` for modules, functions, and variables; `PascalCase` for classes and Pydantic schemas.

## Testing Guidelines

There is currently no dedicated test directory. For every change, run `make test` at minimum. When adding tests, place them under `tests/`, name files `test_*.py`, and keep imports resolvable through the configured `pythonpath = ["src"]`. Prefer focused tests around use cases, API routers, and converter behavior.

## Commit & Pull Request Guidelines

Recent commit history uses short, lowercase summary messages such as `review`, `infra`, `architecture`, and `frontend`. Keep commits concise and scoped to one logical change. Pull requests should include a brief description, validation steps such as `make test`, linked issues when applicable, and screenshots or sample request/response payloads for user-visible API or generated-output changes.

## Security & Configuration Tips

Do not commit `.env` or real API keys. Use `.env.example` as the template for local overrides, LLM credentials, proxy settings, and generated-file storage options. Keep non-secret defaults in `src/common/config/settings/settings*.toml`.

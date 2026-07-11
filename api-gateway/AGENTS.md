# Repository Guidelines

## Project Structure & Module Organization

This repository contains the `vn1-api-gateway` FastAPI service. Runtime code lives under `src/`:

- `src/app/api/`: FastAPI app setup, routers, schemas, dependencies, and error handling.
- `src/app/use_cases/`: application orchestration for chat routing and generator proxying.
- `src/domain/`: domain models, auth logic, and service selection rules.
- `src/infrastructure/clients/`: HTTP/SSE clients for upstream services.
- `src/common/`: shared exceptions, enums, SSE helpers, and Dynaconf settings.
- `.env.example`, `Dockerfile`, and `docker-compose.yaml`: local and container configuration.

No dedicated `tests/` directory is present yet. Add tests under `tests/` for behavior that can run without live upstream services.

## Build, Test, and Development Commands

- `make run`: sync dependencies, load `.env` if present, and run in `DEV` mode on `PORT` or `8000`.
- `make run-prod`: run locally with `API_MODE=PROD`.
- `make test`: run Ruff checks on `src/` and compile all Python modules.
- `uv sync`: install project and development dependencies from `pyproject.toml`.
- `docker compose up --build`: build and run the service in containers when testing deployment wiring.

## Coding Style & Naming Conventions

Use Python 3.13 syntax and package imports rooted at `src`. Keep modules organized by layer: API code should call use cases, and use cases should coordinate domain and infrastructure clients. Ruff is configured in `pyproject.toml`; run `make test` before submitting changes. Ruff banned-import rules prevent cross-service package imports such as `generator`, `skills`, `api_gateway`, or monorepo-root imports. Use HTTP/SSE contracts through gateway clients instead.

Prefer `snake_case` for modules, functions, and variables; `PascalCase` for classes and Pydantic-style schemas; and explicit, descriptive router/use-case names such as `route_chat_stream.py`.

## Testing Guidelines

Current verification is linting plus `compileall`. When adding tests, use `pytest` conventions prepared in `pyproject.toml`: name files `tests/test_*.py`, keep fixtures close to the behavior under test, and mock network dependencies.

## Commit & Pull Request Guidelines

Recent commits use short, lowercase summary messages such as `review`, `frontend`, `infra`, and `architecture`. Keep commits focused and use a concise imperative or descriptive subject. Pull requests should include the intent, affected endpoints or flows, configuration changes, and verification performed, for example `make test` or relevant manual API checks.

## Security & Configuration Tips

Do not commit real secrets. Copy `.env.example` to `.env` for local values. Keep environment-specific settings in `src/common/config/settings/settings.*.toml` and avoid hardcoding upstream service URLs, tokens, or mode-specific behavior in application code.

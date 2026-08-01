# Project Rules

## 1. Стек И Команды

- Python 3.13, FastAPI, Uvicorn, Dynaconf, HTTPX, LangChain OpenAI.
- Зависимости: `uv` и lockfile `uv.lock`.
- Установка зависимостей: `uv sync`.
- Dev run: `make run` (`API_MODE=DEV`, default `PORT=8000`).
- Prod-like local run: `make run-prod`.
- Quality gate: `make test` (`ruff check src` + `compileall`).
- Container check: root `make test` и service restart через `make restart SERVICE=api-gateway`.

## 2. Конвенции

- API layer: `src/app/api`.
- Orchestration: `src/app/use_cases`.
- Domain models/auth/routing rules: `src/domain`.
- Upstream clients: `src/infrastructure/clients`.
- Settings: `src/common/config/settings/settings*.toml`; secrets и upstream URLs только из env/settings.
- Python naming: `snake_case` для modules/functions/variables, `PascalCase` для classes и Pydantic schemas.

## 3. Инварианты

- Gateway является единой backend-точкой frontend, но не владеет бизнес-логикой generator/auth/skills.
- Cross-service Python imports запрещены: `generator`, `skills`, `api_gateway`, `vn1_bot`.
- Generator/auth/skills вызываются только через HTTP/SSE clients.
- SSE-контракт обязан соответствовать `../shared/docs/protocol/sse-stream.md`.
- HTTP-ошибки обязаны соответствовать `../shared/docs/protocol/error-protocol.md`.
- Routing через LLM обязан fallback-иться в обычную chat-ответку, если LLM не выбрала skill/tool.
- В логи не уходят bearer tokens, cookies, OpenAI/GitLab keys и полный user payload без redaction.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `api-gateway/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `api-gateway/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `api-gateway/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый proxy route: router/schema в `src/app/api`, client в `src/infrastructure/clients`, timeout/error mapping.
- Новый skill: enum/config в gateway + URL/settings + SSE handling + запись в `skills/docs/rules.md`.
- Новый router prompt/tool: prompt/config рядом с orchestration code, tests или ручной сценарий для fallback.
- Новый auth-dependent flow: использовать gateway user/context dependency, не парсить JWT в use case повторно.
- Новый runbook: `api-gateway/docs/runbooks`.

## 5. Что Не Автоматизировать Без Согласования

- Изменение public `/api/*` route shape для frontend.
- Изменение SSE terminal event или `event: set` payload.
- Добавление нового upstream/skill без compose/settings update.
- Смена LLM model, tool-binding strategy или fallback behavior для orchestrator.

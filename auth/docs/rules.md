# Project Rules

## 1. Стек И Команды

- Python 3.13, FastAPI, Uvicorn, Dynaconf, HTTPX.
- Auth provider: Keycloak integration в `src/infrastructure/keycloak`.
- Зависимости: `uv` и lockfile `uv.lock`.
- Установка зависимостей: `uv sync`.
- Dev run: `make run` (`API_MODE=DEV`, default `PORT=8030`).
- Prod-like local run: `make run-prod`.
- Quality gate: `make test` (`ruff check src` + `compileall`).

## 2. Конвенции

- API layer: `src/app/api`, routers/schemas/dependencies рядом с FastAPI app.
- Общие ошибки, settings и utilities: `src/common`.
- Provider-specific код держать в `src/infrastructure/keycloak`.
- Settings defaults: `src/common/config/settings/settings.toml`, mode overrides в `settings.dev.toml` и `settings.prod.toml`.
- Python naming: `snake_case` для modules/functions/variables, `PascalCase` для classes и Pydantic schemas.

## 3. Инварианты

- Auth-service владеет только login, refresh, logout, me/context и связью с Keycloak.
- Cross-service Python imports запрещены: `api_gateway`, `generator`, `skills`, `vn1_bot`.
- HTTP-ошибки соответствуют `../shared/docs/protocol/error-protocol.md`.
- Cookies, JWT claims, CORS и refresh behavior не менять без отдельного spec с security criteria.
- В логи никогда не уходят access/refresh tokens, client secrets, passwords, full authorization headers.
- Keycloak realm/client secrets не коммитить; `.env.example` содержит только имена обязательных переменных.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `auth/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `auth/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `auth/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый auth endpoint: router/schema в `src/app/api` + provider boundary в infrastructure, если нужен Keycloak.
- Новый claim/role: spec + обновление context response + проверка потребителей в gateway/frontend.
- Новый auth provider: отдельный infrastructure adapter, без изменения public API до принятого decision record.
- Новый тест: `tests/test_*.py`, без реальных secrets и живого production Keycloak.

## 5. Что Не Автоматизировать Без Согласования

- Изменение cookie names, TTL, SameSite/Secure flags и token refresh policy.
- Изменение Keycloak realm export или client scopes.
- Создание пользователей, ролей или clients в production Keycloak.
- Смена auth provider или public auth contract.

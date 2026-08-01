# Project Rules

## 1. Стек И Команды

- Python 3.13, FastAPI, Uvicorn, Dynaconf, LangChain/LangGraph.
- Зависимости: `uv` и lockfile `uv.lock`.
- Установка зависимостей: `uv sync`.
- Dev run: `make run` (`API_MODE=DEV`, default `PORT=8010`).
- Prod-like local run: `make run-prod`.
- Quality gate: `make test` (`ruff check src` + `compileall`).
- Service orchestration: `make prod`, `make restart`, `make stop` через root Makefile.

## 2. Конвенции

- Runtime-код только в `src/`.
- API layer: `src/app/api/routers`, schemas в `src/app/api/schemas`.
- Use cases: `src/app/use_cases`.
- Domain services/auth helpers: `src/domain`.
- LLM, converter, observability и внешние integrations: `src/infrastructure`.
- Settings: `src/common/config/settings/settings*.toml`; secrets только через env/.env.
- Python naming: `snake_case` для modules/functions/variables, `PascalCase` для classes и Pydantic schemas.

## 3. Инварианты

- Cross-service Python imports запрещены Ruff banned imports: `api_gateway`, `skills`, `generator`, `vn1_bot`.
- Межсервисное взаимодействие только по HTTP/SSE contracts.
- HTTP-ошибки соответствуют `../shared/docs/protocol/error-protocol.md`.
- В логи не уходят API keys, LLM provider payloads с приватным текстом, access tokens и полные пользовательские файлы.
- Новые request models должны явно валидировать режимы ввода. Если endpoint принимает файл или текст, ровно один источник обязателен.
- LLM/provider настройки, proxy и storage paths нельзя хардкодить в use cases.
- Изменения generated-output contract требуют spec в `generator/docs/specs/todo/<feature-name>/spec.md`.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `generator/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `generator/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `generator/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый endpoint: router в `src/app/api/routers`, schema в `src/app/api/schemas`, use case в `src/app/use_cases`.
- Новый LLM provider или converter: adapter в `src/infrastructure`, settings в `src/common/config/settings`, пример env в `.env.example`.
- Новый prompt: хранить в `src/app/prompts` или существующем prompt-модуле, не вшивать большие инструкции в use case.
- Новый тест: `tests/test_*.py`, pythonpath уже настроен на `src` и `../shared/python`.
- Новый document/input flow: spec + sample request/response payload.

## 5. Что Не Автоматизировать Без Согласования

- Установку новых LLM/converter dependencies.
- Изменение public API response shape для frontend.
- Изменение storage layout для загруженных/сгенерированных файлов.
- Автоматическую отправку пользовательского текста во внешние providers без явного product/security решения.

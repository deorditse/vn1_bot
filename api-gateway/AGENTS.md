# Правила Репозитория

## Структура Проекта

Этот каталог содержит FastAPI-сервис `vn1-api-gateway`. Runtime-код находится в `src/`:

- `src/app/api/`: создание FastAPI app, routers, schemas, dependencies и обработка ошибок.
- `src/app/use_cases/`: прикладная orchestration для chat routing и proxy в generator.
- `src/domain/`: domain models, auth-логика и правила выбора сервиса.
- `src/infrastructure/clients/`: HTTP/SSE-клиенты для upstream-сервисов.
- `src/common/`: общие исключения, enums и Dynaconf settings.
- `.env.example`, `Dockerfile`, `docker-compose.yaml`: локальная и контейнерная конфигурация.

Отдельного каталога `tests/` пока нет. Новые тесты добавляй в `tests/`, если поведение можно проверить без живых upstream-сервисов.

## Команды

- `make run`: синхронизировать зависимости, загрузить `.env` при наличии и запустить сервис в `DEV` mode на `PORT` или `8000`.
- `make run-prod`: локально запустить сервис с `API_MODE=PROD`.
- `make test`: запустить Ruff checks для `src/` и скомпилировать Python-модули.
- `uv sync`: установить project и dev dependencies из `pyproject.toml`.
- `docker compose up --build`: собрать и запустить сервис в контейнерах для проверки deployment wiring.

## Стиль Кода

Используй Python 3.13 и package imports от корня `src`. Держи слои разделенными: API вызывает use cases, а use cases координируют domain и infrastructure clients. Ruff настроен в `pyproject.toml`; перед сдачей изменений запускай `make test`. Ruff banned-import rules запрещают cross-service package imports вроде `generator`, `skills`, `api_gateway` и импортов от корня монорепозитория. Межсервисное взаимодействие должно идти через HTTP/SSE contracts.

Используй `snake_case` для modules, functions и variables, `PascalCase` для classes и Pydantic schemas. Router/use-case имена должны явно описывать назначение, например `stream_skill.py`.

## Тестирование

Сейчас базовая проверка состоит из linting и `compileall`. При добавлении тестов используй pytest conventions из `pyproject.toml`: файлы `tests/test_*.py`, fixtures рядом с проверяемым поведением, сетевые зависимости мокать.

## Commits И Pull Requests

Последние commits используют короткие lowercase summaries вроде `review`, `frontend`, `infra`, `architecture`. Держи commits сфокусированными. Pull request должен описывать цель, затронутые endpoints или flows, изменения конфигурации и выполненную проверку, например `make test` или ручные API checks.

## Безопасность И Конфигурация

Не коммить реальные secrets. Для локальных значений копируй `.env.example` в `.env`. Environment-specific settings держи в `src/common/config/settings/settings.*.toml`; не hardcode upstream URLs, tokens и mode-specific поведение в application code.

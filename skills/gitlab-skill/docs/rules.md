# Project Rules

## 1. Стек И Команды

- Python 3.13, FastAPI, Uvicorn, Dynaconf, HTTPX, LangGraph, LangChain OpenAI, PyYAML.
- Зависимости: `uv` и lockfile `uv.lock`.
- Установка зависимостей: `uv sync`.
- Dev run: `make run` или service-level команда из README.
- Quality gate: `make test` (`ruff check src` + `compileall`).
- Container restart из корня: `make restart SERVICE=gitlab-skill`.

## 2. Конвенции

- Runtime-код только в `src/`.
- Prompts: `src/infrastructure/gitlab/prompts`.
- Settings/config: `src/common/config/settings/settings*.toml`.
- GitLab API access держать в infrastructure layer.
- Workflow nodes должны возвращать typed state/structured result, а не свободные dict без схемы.
- Python naming: `snake_case` для modules/functions/variables, `PascalCase` для classes и Pydantic schemas.

## 3. Инварианты

- Ответ строится только на найденных GitLab files/snippets/metadata; неподтвержденный код не выдумывать.
- Cross-service imports запрещены: `api_gateway`, `generator`, sibling `skills`, `vn1_bot`.
- SSE-события соответствуют `../../../shared/docs/protocol/sse-stream.md`.
- HTTP-ошибки соответствуют `../../../shared/docs/protocol/error-protocol.md`.
- Repository list и repository descriptions берутся из settings/config, не из prompt hardcode.
- Правила выбора репозитория, file role descriptions и response format должны жить в prompts/config, не в Python branching.
- В логи и ответы не уходят `GITLAB_TOKEN`, приватные internal URLs сверх source URL и данные вне scope запроса.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/gitlab-skill/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/gitlab-skill/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/gitlab-skill/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый repository: settings entry с id/name/url/description + проверка repository selector prompt.
- Новый prompt rule: YAML в `src/infrastructure/gitlab/prompts` + spec, если меняется routing/answer behavior.
- Новый workflow node: `src/app/workflows/gitlab_skill/nodes` + typed state update + focused test/manual trace.
- Новый GitLab endpoint: infrastructure client method + timeout/error mapping.
- Новый answer format: prompt update, `build_response` contract и example output в spec.

## 5. Что Не Автоматизировать Без Согласования

- Поиск по всем repositories, если пользователь явно ограничил repo/layer и selector уверен.
- Изменение fallback behavior, когда источники не найдены.
- Массовую индексацию GitLab или сохранение snippets вне approved storage.
- Добавление write actions в GitLab: comments, commits, labels, merge requests.

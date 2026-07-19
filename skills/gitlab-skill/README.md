# gitlab-skill

Skill для поиска по коду в разрешенных GitLab-репозиториях.

## Текущий Режим

Код сервиса находится в `src/`.

FastAPI-сервис отдает SSE:

- `GET /health`
- `GET /manifest`
- `POST /v1/run/stream`

Поиск работает через GitLab API:

```text
GET /api/v4/projects/:id/search?scope=blobs&search=...
```

Связка:

```text
frontend -> api-gateway -> gitlab-skill -> SSE
```

## Локальный Запуск

```bash
make run
make run-prod
make prod
make test
make restart
make stop
```

## Config

Runtime-настройки лежат в:

```text
src/common/config/settings/
```

`settings.toml` содержит дефолты и список разрешенных GitLab-репозиториев.
`settings.dev.toml` и `settings.prod.toml` переопределяют их по `API_MODE`.
Локальный `.env` необязателен и нужен только для секретов или локальных override.

Пример репозитория в `settings.toml`:

```toml
[[default.GITLAB_REPOSITORIES]]
id = "flutter_mobile_vn1"
base_url = "https://gitlab.avgr.su"
project_path = "amiga/flutter_mobile_vn1"
token_env = "GITLAB_AVGR_TOKEN"
enabled = true

[[default.GITLAB_REPOSITORIES]]
id = "backend_vn1"
base_url = "https://gitlab.avgr.su"
project_path = "amiga/vn1"
token_env = "GITLAB_AVGR_TOKEN"
enabled = true
```

Несколько репозиториев задаются несколькими TOML-блоками:

```toml
[[default.GITLAB_REPOSITORIES]]
id = "flutter_mobile_vn1"
base_url = "https://gitlab.avgr.su"
project_path = "amiga/flutter_mobile_vn1"
token_env = "GITLAB_AVGR_TOKEN"
enabled = true

[[default.GITLAB_REPOSITORIES]]
id = "backend_vn1"
base_url = "https://gitlab.avgr.su"
project_path = "amiga/vn1"
token_env = "GITLAB_AVGR_TOKEN"
enabled = true
per_project_limit = 5
```

Для входного вопроса skill сначала просит LLM выбрать список репозиториев для поиска:

- вопросы только про мобильное приложение ищутся в `flutter_mobile_vn1`;
- вопросы только про backend ищутся в `backend_vn1`;
- cross-cutting вопросы могут искать сразу в нескольких репозиториях;
- если область неясна, поиск идет по всем enabled-репозиториям.

Node `select_repositories` вызывает легкую модель со structured output-схемой `RepositorySelection` и кладет `selected_repository_ids` в graph state. Conditional edge после этой node передает выполнение в `search_gitlab` только когда список репозиториев выбран.

Если `GITLAB_QUERY_PLANNER_PROVIDER` не равен `openai`, не задан `OPENAI_API_KEY` или LLM вернула некорректный ответ, skill не пытается классифицировать вопрос локально и ищет по всем enabled-репозиториям.
Модель для этой легкой классификации задается через `GITLAB_REPOSITORY_SELECTOR_MODEL`.

Минимальный `.env` для этого GitLab:

```env
GITLAB_AVGR_TOKEN=glpat-...
OPENAI_API_KEY=sk-...
```

В `API_MODE=DEV` токены не проверяются при старте сервиса. В `API_MODE=PROD` при выключенном mock-режиме все `token_env` из enabled-репозиториев должны быть заданы в `.env` или окружении контейнера. Если `GITLAB_QUERY_PLANNER_PROVIDER = "openai"`, также должен быть задан `OPENAI_API_KEY`.

## Semantic Query Planner

GitLab API выполняет lexical code search, поэтому для запросов на естественном языке skill сначала строит набор поисковых code-терминов. По умолчанию включен OpenAI-compatible planner:

```toml
GITLAB_QUERY_PLANNER_PROVIDER = "openai"
GITLAB_QUERY_PLANNER_MODEL = "gpt-4o-mini"
GITLAB_REPOSITORY_SELECTOR_MODEL = "gpt-4o-mini"
GITLAB_QUERY_PLANNER_BASE_URL = "https://api.openai.com/v1"
GITLAB_QUERY_PLANNER_TOKEN_ENV = "OPENAI_API_KEY"
GITLAB_QUERY_PLANNER_MAX_QUERIES = 6
GITLAB_QUERY_PLANNER_MIN_WORDS = 3
GITLAB_ANSWER_USE_LLM = false
GITLAB_ANSWER_MAX_SOURCES = 8
GITLAB_ANSWER_MAX_DESCRIPTION_CHARS = 120
```

Для экономии токенов planner не вызывает LLM для коротких code-like запросов вроде `AuthService`, `auth_token` или `login`. Повторные одинаковые запросы кешируются в памяти процесса.

Если внешний planner не нужен, можно переключить на простой fallback:

```toml
GITLAB_QUERY_PLANNER_PROVIDER = "fallback"
```

Fallback не делает семантическое расширение: он ищет исходную фразу и выделенные из нее code-like токены.

Тот же LLM-сервис может использоваться для финального ответа, если включить `GITLAB_ANSWER_USE_LLM = true`. По умолчанию финальный ответ строится без LLM, чтобы не тратить токены: skill возвращает детерминированный список найденных мест с репозиторием, файлом, строкой и ссылкой.

Если нужен второй репозиторий или другой GitLab-инстанс, добавляется еще один блок:

```toml
[[default.GITLAB_REPOSITORIES]]
id = "another_repo"
base_url = "https://gitlab.example.ru"
project_path = "group/another_repo"
token_env = "GITLAB_EXAMPLE_TOKEN"
enabled = true
```

## Docker

```text
Dockerfile
docker-compose.yaml
```

Корневой `docker-compose.yml` подключает этот skill через `skills/docker-compose.yaml`.

## Errors

HTTP-ошибки и SSE-протокол описаны в `../../docs/ERROR_PROTOCOL.md`.

Skill должен завершать поток терминальным событием:

```text
data: {"data":{"fragment_id":1,"fragment_type":"think","status":"in_progress","streaming":false,"content":"### Ищу..."}}
data: {"data":{"fragment_id":1,"fragment_type":"think","status":"success","streaming":false,"content":"### Найдено..."}}
data: {"data":{"status":"success","fragments":[...]}}
```

## Источники

Сейчас используются результаты `scope=blobs`, то есть поиск по коду.
Skill возвращает ссылки на конкретные файлы и строки в GitLab UI, а также структурированные поля источника:

- `repository_id`
- `project_path`
- `file_path`
- `ref`
- `line`
- `url`

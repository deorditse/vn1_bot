# gitlab-skill

Будущий skill для поиска по GitLab.

## Текущий Режим

Код сервиса находится в `src/`.

Сейчас это минимальный FastAPI-сервис с SSE:

- `GET /health`
- `GET /manifest`
- `POST /v1/run/stream`

Реальный GitLab API пока не подключен. Поиск возвращает placeholder-source, чтобы проверить связку:

```text
frontend -> api-gateway -> gitlab-skill -> SSE
```

FastAPI здесь нужен как простой HTTP/SSE transport. Внутри skill позже можно добавить LangGraph, MCP-клиенты или прямой GitLab API adapter без изменения внешнего контракта.

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

`settings.toml` содержит дефолты, `settings.dev.toml` и `settings.prod.toml` переопределяют их по `API_MODE`.
Локальный `.env` необязателен и нужен для `GITLAB_TOKEN` или override.

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

## Планируемые Источники

- issues;
- merge requests;
- repositories;
- README;
- code;
- discussions.

Skill должен возвращать ссылки на конкретные GitLab-артефакты как подтверждающие источники.

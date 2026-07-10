# generator

Текущий рабочий Python backend, перенесенный из прежнего корня репозитория.

## Состав

- `src/` - исходный код backend;
- `pyproject.toml` - зависимости проекта;
- `uv.lock` - lock-файл зависимостей;
- `.python-version` - версия Python для локальной разработки;
- `Dockerfile` - сборка контейнера generator;
- `Makefile` - команды локального запуска и обслуживания generator;
- `.env.example` - пример переменных окружения;
- `.env` - локальные секреты и настройки, не коммитится;
- `docs/` - старая документация и примеры generator.

## Локальный Запуск

```bash
cd generator
cp .env.example .env
make sync
make run-local
```

По умолчанию API запускается на порту `8010`.

## Docker Compose

Общий `docker-compose.yml` находится в корне монорепозитория, потому что поднимает не только `generator`, но и `frontend`, `nginx`, `keycloak`, `certbot`.

Из папки `generator` можно запускать общий compose через Makefile:

```bash
make run
make docker-logs-backend
make docker-down
```

Эквивалентный прямой запуск из корня:

```bash
docker compose --env-file generator/.env -f docker-compose.yml up -d --build
```

## Keycloak

Keycloak realm export теперь находится в:

```text
../auth/keycloak/realm-export.json
```

В compose он монтируется в контейнер Keycloak автоматически.

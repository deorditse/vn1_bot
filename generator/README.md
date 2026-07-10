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

Код сервиса находится в `src/`.

```bash
cd generator
make run
```

`.env` необязателен. Если нужны локальные секреты, создайте его вручную по примеру `.env.example`.

По умолчанию API запускается на порту `8010`.

В `API_MODE=DEV` generator не требует Bearer-токен от Gateway и использует локального dev-пользователя. Это нужно только для локальной разработки и прямого тестирования сервиса.

## Config

Runtime-настройки лежат в:

```text
src/common/config/settings/
```

`settings.toml` содержит дефолты, `settings.dev.toml` и `settings.prod.toml` переопределяют их по `API_MODE`.
Локальный `.env` необязателен и нужен для LLM-ключей, proxy и точечных override.

## Docker Compose

Корневой `docker-compose.yml` содержит только nginx/proxy.
Сам `generator` описан в `generator/docker-compose.yaml`, а полный стенд собирается через корневой `Makefile`.

Из корня монорепозитория:

```bash
make prod
make restart SERVICE=backend-vn1
make stop
```

Из папки `generator` старый Makefile тоже работает:

```bash
make run
make run-prod
make prod
make test
make restart
make stop
```

## Keycloak

Generator больше не содержит login/refresh endpoints. Для user context он использует
только переданный Bearer-токен и при необходимости обращается к `auth-service` context.

`api-gateway` передает в generator только исходный security context:

```text
Authorization: Bearer <access_token>
```

Пример прямого получения user context в PROD:

```bash
curl -H 'Authorization: Bearer <access_token>' http://localhost:8030/v1/auth/context
```

Если generator нужен пользователь для `owner_id` или audit, он получает его по токену через
`auth-service` context. URL задается через `AUTH_CONTEXT_URL`.

Login/refresh находятся в `auth`, проверка доступа к `/api` и skills находится в `api-gateway`.

## Errors

HTTP-ошибки возвращаются в общем формате из `../docs/ERROR_PROTOCOL.md`.

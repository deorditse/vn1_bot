# vn1_bot

Монорепозиторий VN1 с frontend, generator, auth-service, api-gateway, Keycloak и skill-сервисами. Внешняя точка входа для контейнерного стенда - root `nginx` из `docker-compose.yml`.

## Текущая Схема

```text
Browser
  |
  | http://<host>/
  v
root nginx :80/:443
  |
  +-- /                  -> frontend:80
  |
  +-- /auth/*            -> auth-service:8030/v1/auth/*
  |                         auth-service
  |                         - login / refresh / logout / me / context
  |                         - ставит httpOnly cookies vn1_access_token и vn1_refresh_token
  |                         - ходит в Keycloak
  |
  +-- /api/*             -> api-gateway:8000/*
  |                         api-gateway
  |                         - единая backend-точка для frontend
  |                         - принимает Authorization Bearer или cookie vn1_access_token
  |                         - проксирует /generator/* в generator
  |                         - вызывает skills
  |
  +-- /keycloak/*        -> keycloak:8080/keycloak/*
                            Keycloak realm vn1

api-gateway:8000
  |
  +-- auth-service:8030/v1/auth/context
  +-- backend-vn1:8010
  +-- gitlab-skill:8022

backend-vn1:8010
  |
  +-- auth-service:8030/v1/auth/context
  +-- OpenAI / other LLM providers

gitlab-skill:8022
  |
  +-- GitLab API
```

## Публичные Адреса

Все публичные запросы идут через `nginx`.

```text
http://<host>/                    frontend
http://<host>/auth/*              auth-service
http://<host>/api/*               api-gateway, включая /api/generator/*
http://<host>/keycloak/*          Keycloak через nginx
http://<host>:8080/keycloak/*     Keycloak напрямую
```

Внутренние адреса доступны только внутри docker-сети `vn1`:

```text
frontend:80
backend-vn1:8010
auth-service:8030
api-gateway:8000
gitlab-skill:8022
keycloak:8080
```

## Структура

```text
frontend/          React/Vite frontend
generator/         текущий generator backend, compose service backend-vn1
auth/              auth-service и Keycloak realm export
api-gateway/       gateway для /api и skills
skills/            skill-сервисы, сейчас gitlab-skill
shared/            certbot, общая инфраструктура, shared/python protocol contracts
docs/protocol/     межсервисные protocol contracts
docs/              общая документация
nginx.conf         root nginx routing
docker-compose.yml root nginx и общая сеть
Makefile           единая точка запуска compose-файлов
```

## Frontend Env

Frontend использует значения из `frontend/.env.example` как дефолты проекта. Если нужен override, создайте `frontend/.env`.

```env
API_BASE_URL=/api
AUTH_BASE_URL=/auth

DEV_PROXY_API_TARGET=http://localhost:8000
DEV_PROXY_AUTH_TARGET=http://localhost:8030
```

## Секреты

`.env` файлы не коммитятся. Для запуска generator нужен `generator/.env`:

```bash
cp generator/.env.example generator/.env
```

Минимально:

```env
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=
GIGACHAT_API_KEY=
```

Для GitLab skill:

```env
GITLAB_BASE_URL=https://gitlab.com
GITLAB_TOKEN=...
```

## Запуск

Проверить compose-конфигурацию:

```bash
make test
```

Поднять полный стенд:

```bash
make prod
```

Поднять только frontend, generator, auth и root nginx:

```bash
REPO_ROOT=$(pwd) docker compose \
  -f docker-compose.yml \
  -f auth/docker-compose.yaml \
  -f frontend/docker-compose.yaml \
  -f generator/docker-compose.yaml \
  up -d --build
```

Остановить:

```bash
make stop
```

Пересобрать один сервис:

```bash
make restart SERVICE=backend-vn1
make restart SERVICE=frontend
make restart SERVICE=auth-service
```

## Проверки

```bash
curl http://localhost/
curl http://localhost/api/health
curl http://localhost/auth/me
```

Проверить, что `OPENAI_API_KEY` попал в generator container:

```bash
docker exec vn1_bot-backend-vn1-1 sh -c 'test -n "$OPENAI_API_KEY" && echo OPENAI_API_KEY=set || echo OPENAI_API_KEY=empty'
```

Тестовый пользователь Keycloak из realm export:

```text
login: vn1-user
password: vn1-user
```

## Auth

Browser auth работает через httpOnly cookies:

```text
vn1_access_token
vn1_refresh_token
```

Browser-facing сервисы принимают токен единообразно:

```text
Authorization: Bearer <token>
или cookie vn1_access_token
```

Это поддержано в:

```text
auth-service: /me, /context, /userinfo
api-gateway: /api/*
generator: /generator/generate/*, когда вызывается gateway
```

`gitlab-skill` сейчас внутренний сервис и вызывается через `api-gateway`.

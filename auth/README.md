# Auth

Основной auth-сервис проекта.

## Состав

- `src/` - auth-service API: login, refresh, logout, userinfo.
- `src/` - код сервиса.
- `src/infrastructure/keycloak/` - реализация текущего auth provider-а.
- `docker-compose.yaml` - compose-фрагмент auth-service и Keycloak.

## Ответственность

Код сервиса находится в `src/`.

- browser endpoints для frontend: `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`;
- сервисные endpoints для внутренних клиентов: `/v1/auth/token`, `/v1/auth/refresh-token`, `/v1/auth/context`, `/v1/auth/userinfo`;
- установка и очистка `httpOnly` cookies;
- работа с provider-ом авторизации.

## Provider

Сейчас provider - Keycloak:

```text
auth/src/infrastructure/keycloak/
```

Позже можно добавить другого provider-а, не меняя внешний auth API.

## Config

Runtime-настройки сервиса лежат в:

```text
src/common/config/settings/
```

`settings.toml` содержит дефолты, `settings.dev.toml` и `settings.prod.toml` переопределяют их по `API_MODE`.
Локальный `.env` необязателен и нужен только для секретов или override.

## Запуск

Auth-service:

```bash
make prod SERVICE=auth-service
```

Keycloak:

```bash
make prod SERVICE=keycloak
```

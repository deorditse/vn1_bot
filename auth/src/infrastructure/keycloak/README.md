# Keycloak Provider

Инфраструктурная реализация auth provider-а для сервиса `auth`.

## Состав

- `realm-export.json` - realm `vn1`, клиент `vn1-api`, роль `vn1-user`, тестовый пользователь.
- `.env.example` - пример переменных окружения Keycloak.

## Роль в Архитектуре

Keycloak выпускает и проверяет токены. Пользовательские auth endpoints живут в сервисе `auth`:

- `/auth/login`
- `/auth/refresh`
- `/auth/logout`
- `/auth/me`

Контейнер Keycloak описан в `auth/docker-compose.yaml` и запускается через корневой Makefile:

```bash
make prod SERVICE=keycloak
```

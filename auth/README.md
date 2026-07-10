# Auth

Auth-инфраструктура проекта.

## Состав

- `keycloak/realm-export.json` - Keycloak realm export, перенесенный из прежнего корня репозитория.

## Ответственность

- конфигурация Keycloak realm;
- роли и тестовые пользователи;
- импорт realm при запуске контейнера Keycloak.

Keycloak поднимается из корневого `docker-compose.yml`.

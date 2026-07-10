# api-gateway

Заготовка под будущий Gateway-сервис.

## Ответственность

- авторизация через Keycloak;
- история чатов;
- пользовательские настройки;
- request metadata;
- graph/orchestrator flow;
- выбор skills;
- вызов skills по HTTP/SSE;
- SSE-прогресс во frontend;
- финальная сборка grounded answer.

## Будущее Хранилище

`gateway-postgres`:

- chats;
- messages;
- user settings;
- skill runs;
- request metadata.

## Граница Ответственности

Gateway не должен напрямую знать детали GitLab, wiki, Figma или product KB. Он выбирает нужный skill, вызывает его по контракту и агрегирует события/источники.

# vn1_bot

Монорепозиторий AI-платформы VN1. Сейчас в нем живет рабочий сервис `generator`, frontend, auth-инфраструктура и заготовки под будущую архитектуру вокруг `api-gateway` и независимых `skills`.

## Текущая Архитектура

```text
frontend
   |
   | HTTPS /api
   v
nginx
   |
   +-- generator
   |   Текущий Python backend.
   |   Сейчас принимает API-запросы frontend, работает с Keycloak и выполняет генерацию.
   |
   +-- auth/keycloak
       Keycloak realm export и контейнер Keycloak из docker-compose.
```

Сейчас `generator` является рабочим backend. Он временно совмещает несколько ответственностей, которые позже будут разнесены:

- backend API для frontend;
- авторизация через Keycloak;
- генерация ответов/файлов;
- текущая бизнес-логика;
- runtime-настройки текущего Python-проекта.

## Структура Монорепозитория

```text
vn1_bot/
  frontend/        # текущий frontend
  generator/       # текущий рабочий Python backend
  api-gateway/     # будущая единая backend-точка входа
  skills/          # будущие независимые сервисы-навыки
  auth/            # Keycloak и auth-инфраструктура
  shared/          # общая инфраструктура: certbot, xray config, ci-cd
  docs/            # общая документация проекта
  docker-compose.yml
  nginx.conf
```

Коротко по слоям:

- `frontend` показывает UI, ход выполнения, результаты, источники и работает через `/api`.
- `generator` сохраняет текущую работоспособность проекта до миграции.
- `api-gateway` станет единственной backend-точкой входа для frontend.
- `skills` будут отдельными сервисами, которые Gateway вызывает по единому HTTP/SSE-протоколу.
- `auth` содержит Keycloak-конфигурацию.
- `shared` содержит общие инфраструктурные и CI/CD-файлы, которые не принадлежат конкретному сервису.

## Целевая Архитектура

```text
frontend (https://ai-bot.vn1.ru/)
   |
   | HTTPS /api
   | UI, авторизация, чат, SSE-прогресс, источники.
   v
api-gateway
   |
   +-- gateway-postgres
   |   История чатов, сообщения, настройки пользователей,
   |   skill runs, request metadata.
   |
   +-- telemetry stack
   |   prometheus, grafana, loki/alloy, tempo.
   |
   v
skills
   |
   +-- product-kb-skill
   |   +-- kb-postgres
   |   +-- opensearch
   |
   +-- gitlab-skill
   +-- wiki-skill
   +-- figma-skill
   +-- support-skill
```

`api-gateway` будет отвечать за:

- авторизацию;
- пользовательский контекст;
- историю чатов;
- настройки пользователя;
- выбор skill через graph/orchestrator flow;
- SSE-стримы во frontend;
- вызов skills;
- агрегацию событий;
- финальную сборку ответа;
- метрики, логи и трассировку.

`skills` будут отвечать только за конкретные источники данных. Например, `product-kb-skill` ищет по базе знаний продукта, `gitlab-skill` по GitLab, `wiki-skill` по wiki/Confluence/Notion.

Главное правило для будущих grounded answers:

```text
Нет подтвержденных источников = нет финального ответа.
```

## Как Разнести По Микросервисам

Перенос лучше делать постепенно, без остановки текущего `generator`.

1. Зафиксировать общий HTTP/SSE-контракт skills: manifest, request, stream events, sources, final answer.
2. Поднять минимальный `api-gateway`, который сначала проксирует текущие сценарии в `generator`.
3. Перенести auth, пользовательский контекст и SSE во frontend из `generator` в `api-gateway`.
4. Добавить `gateway-postgres` для истории, сообщений, настроек и metadata.
5. Создать первый реальный skill: `product-kb-skill`.
6. Вынести knowledge base в `product-kb-skill`, `kb-postgres` и OpenSearch.
7. Добавить orchestrator flow в Gateway для выбора одного или нескольких skills.
8. Постепенно добавить `gitlab-skill`, `wiki-skill`, `figma-skill`, `support-skill`.
9. Перенести генерацию финального grounded answer в Gateway.
10. Добавить telemetry stack: Prometheus, Grafana, Loki/Alloy, Tempo.
11. После стабилизации решить судьбу `generator`: оставить как legacy-сервис, превратить в skill или разобрать на новые сервисы.

## Где Смотреть Детали

- [frontend/README.md](frontend/README.md)
- [generator/README.md](generator/README.md)
- [api-gateway/README.md](api-gateway/README.md)
- [skills/README.md](skills/README.md)
- [auth/README.md](auth/README.md)
- [shared/README.md](shared/README.md)
- [docs/README.md](docs/README.md)

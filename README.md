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
   +-- api-gateway
   |   Единая backend-точка входа.
   |   Сейчас проксирует старые endpoints в generator и умеет вызывать skills по SSE.
   |
   +-- auth
   |   Внутренний auth facade: login, refresh, logout, userinfo поверх Keycloak.
   |
   +-- generator
   |   Текущий Python backend.
   |   Пока содержит старые API-сценарии и генерацию.
   |
   |   Keycloak provider лежит в auth/src/infrastructure/keycloak.
   |
   +-- skills/gitlab-skill
       Первый пример skill-сервиса с HTTP/SSE-контрактом.
```

Сейчас `api-gateway` уже должен быть входной точкой для клиентов. Старые frontend-запросы `/api/*` проходят через Gateway и fallback-проксируются в `generator`.
Авторизация frontend идет через публичный префикс `/auth/*` в `auth-service`; cookie ставится как `httpOnly` на тот же домен и затем читается `api-gateway` при запросах `/api/*`.

`generator` пока остается рабочим backend и временно содержит старые сценарии, которые позже будут разнесены:

- backend API для frontend;
- генерация ответов/файлов;
- текущая бизнес-логика;
- runtime-настройки текущего Python-проекта.

## Структура Монорепозитория

```text
vn1_bot/
  frontend/        # текущий frontend
  generator/       # текущий рабочий Python backend
  api-gateway/     # единая backend-точка входа
  skills/          # будущие независимые сервисы-навыки
  auth/            # auth-service; provider Keycloak внутри src/infrastructure/keycloak
  shared/          # общая инфраструктура: certbot, xray config, ci-cd
  docs/            # общая документация проекта
  docker-compose.yml # только nginx/proxy и общая сеть
  nginx.conf
```

Коротко по слоям:

- `frontend` показывает UI, ход выполнения, результаты, источники и работает через `/api`.
- `generator` сохраняет текущую работоспособность проекта до миграции.
- `api-gateway` является единственной backend-точкой входа для frontend.
- `skills` будут отдельными сервисами, которые Gateway вызывает по единому HTTP/SSE-протоколу.
- Skills перечислены в enum Gateway и подключаются через `api-gateway/src/app/config/setting.toml`.
- `auth` содержит `auth-service` и provider Keycloak в `auth/src/infrastructure/keycloak`.
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
   +-- auth-service
   |   login, refresh, logout, userinfo поверх Keycloak.
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

- browser-cookie auth facade;
- проверку access token и ролей;
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

Frontend может получить список включенных skills через Gateway и передать в чат `available_skills`, чтобы Gateway выбирал только из разрешенных навыков.

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

Единый формат ошибок описан в [docs/ERROR_PROTOCOL.md](docs/ERROR_PROTOCOL.md).

## Запуск

Корневой `docker-compose.yml` содержит только общий nginx/proxy и сеть `vn1`.
Сервисы подключаются compose-файлами своих слоев, а запуск идет через корневой `Makefile`.

```bash
make prod
make restart
make stop
make test
```

Для одного сервиса используйте `SERVICE`:

```bash
make prod SERVICE=frontend
make restart SERVICE=gitlab-skill
make stop SERVICE=api-gateway
```

Внутри сервисов есть свои Makefile с одинаковыми базовыми командами:

```bash
make run
make run-prod
make test
make prod
make restart
make stop
```

`.env` файлы не создаются автоматически. Если сервису нужны локальные секреты, создайте `.env` вручную по соответствующему `.env.example`.

Для локальной разработки используется dev-режим:

```text
api-gateway/.env: API_MODE=DEV
generator/.env: API_MODE=DEV
skills/gitlab-skill/.env: API_MODE=DEV
```

В этом режиме Gateway не проверяет токены Keycloak, `auth` может ставить dev-сессию, а `generator` принимает локального dev-пользователя без Bearer-токена. По умолчанию в `.env.example` стоит `API_MODE=PROD`, поэтому dev bypass включается только явно.

Доступ к skills фильтруется в Gateway по ролям пользователя из Keycloak и `required_roles` в `api-gateway/src/app/config/setting.toml`.

Под капотом `Makefile` подключает:

```text
docker-compose.yml
shared/docker-compose.yaml
auth/docker-compose.yaml
frontend/docker-compose.yaml
generator/docker-compose.yaml
skills/docker-compose.yaml
api-gateway/docker-compose.yaml
```

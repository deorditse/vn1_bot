# api-gateway

Заготовка под будущий Gateway-сервис.

## Ответственность

- чтение auth cookie от frontend;
- проверка access token и ролей;
- история чатов;
- пользовательские настройки;
- request metadata;
- graph/orchestrator flow;
- выбор skills;
- вызов skills по HTTP/SSE;
- SSE-прогресс во frontend;
- финальная сборка grounded answer.

## Текущий Режим

Сейчас Gateway работает как единая входная точка `/api`:

- `/chat/stream` - новый Gateway endpoint для SSE-маршрутизации;
- `/skills` и `/skills/available` - список доступных skills для frontend;
- `/skills/{skill_id}/stream` - прямое SSE-проксирование в skill;
- `/skills/{skill_id}/manifest` - manifest конкретного skill;
- `/generator/{path}` - явный proxy в текущий `generator`;
- `/{path}` - fallback proxy в `generator`, чтобы старые frontend endpoints продолжали работать.

Browser auth endpoints живут в `auth-service` и доступны через nginx как `/auth/*`.
В Gateway auth endpoints больше не регистрируются.

## Skills

Известные skills перечислены в enum:

```text
src/common/enums.py
```

Подключение и включение skills задается через TOML:

```text
src/app/config/setting.toml
```

Там же задается доступ по ролям:

```toml
[skills.gitlab]
required_roles = ["vn1-user"]
```

Gateway берет роли из access token Keycloak и показывает/вызывает только те skills, для которых у пользователя есть все `required_roles`.

Пример chat-запроса с ограничением доступных skills:

```json
{
  "request_id": "00000000-0000-0000-0000-000000000001",
  "chat_id": "00000000-0000-0000-0000-000000000002",
  "question": "Найди обсуждение в GitLab",
  "target": "skill",
  "available_skills": ["gitlab"]
}
```

Если `skill_id` передан явно, Gateway попробует вызвать именно его. Если `skill_id` не передан, Gateway выберет skill из `available_skills`.

Если frontend передал `available_skills`, Gateway дополнительно пересекает их со skills, доступными пользователю по ролям.

## Config

Runtime-настройки сервиса лежат в:

```text
src/common/config/settings/
```

`settings.toml` содержит дефолты, `settings.dev.toml` и `settings.prod.toml` переопределяют их по `API_MODE`.
Локальный `.env` необязателен и нужен только для секретов или override.

## Будущее Хранилище

`gateway-postgres`:

- chats;
- messages;
- user settings;
- skill runs;
- request metadata.

## Граница Ответственности

Gateway не должен напрямую знать детали GitLab, wiki, Figma или product KB. Он выбирает нужный skill, вызывает его по контракту и агрегирует события/источники.

## Почему FastAPI

Gateway работает с HTTP/SSE, поэтому FastAPI здесь остается базовым транспортным слоем. Оркестратор, LangGraph flow и бизнес-логика должны жить в `app/use_cases`, `domain/services` и `infrastructure`, а не в роутерах.

## Auth

Gateway не выдает и не обновляет токены напрямую через Keycloak.

Token lifecycle вынесен в:

```text
../auth/
```

Browser auth flow:

```text
frontend -> /auth -> auth-service -> Keycloak
frontend -> /api  -> api-gateway
```

Внутрь `generator` и `skills` Gateway передает только:

```text
Authorization: Bearer <access_token>
```

Пример прямого сервисного вызова:

```bash
curl -H 'Authorization: Bearer <access_token>' http://localhost:8030/v1/auth/context
```

Проверка access token по JWKS остается в Gateway, чтобы быстро фильтровать входящие
frontend-запросы и проверять роли для skills.

## Локальный Запуск

Код сервиса находится в `src/`.

```bash
uv sync
PYTHONPATH=src uv run python src/app/run.py
```

В `API_MODE=DEV` Gateway не проверяет токены Keycloak и использует локального пользователя:

```text
id=dev-user
roles=admin,vn1-user
```

Auth endpoints находятся в сервисе `auth`.

В `PROD` авторизация обязательна: Gateway проверяет токен и наличие ролей из `AUTH_REQUIRED_ROLES`, по умолчанию `vn1-user`.

## Docker

Gateway поднимается compose-файлом своего слоя:

```bash
make prod SERVICE=api-gateway
```

В полном стенде этот файл подключается вместе с root proxy, auth, frontend, generator и skills.

## Make

```bash
make run
make run-prod
make prod
make test
make restart
make stop
```

## Errors

HTTP-ошибки и SSE-протокол skills описаны в `../docs/ERROR_PROTOCOL.md`.

Gateway работает как `chat-service`: промежуточные SSE-события skill пропускает наружу, терминальный `data.status=success|error` с `fragments` перехватывает и заменяет финальным `event: set` с message payload.

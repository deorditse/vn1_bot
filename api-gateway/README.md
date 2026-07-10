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

## Текущий Режим

Сейчас Gateway работает как единая входная точка `/api`:

- `/auth/login` - login через Keycloak, выставляет auth cookies;
- `/auth/refresh` - обновляет access/refresh cookies;
- `/auth/logout` - очищает auth cookies;
- `/auth/me` - возвращает текущего пользователя;
- `/chat/stream` - новый Gateway endpoint для SSE-маршрутизации;
- `/skills` и `/skills/available` - список доступных skills для frontend;
- `/skills/{skill_id}/stream` - прямое SSE-проксирование в skill;
- `/skills/{skill_id}/manifest` - manifest конкретного skill;
- `/generator/{path}` - явный proxy в текущий `generator`;
- `/{path}` - fallback proxy в `generator`, чтобы старые frontend endpoints продолжали работать.

Это позволяет поставить Gateway перед frontend уже сейчас, не ломая текущий `generator`.

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

## Keycloak Admin API

Пока Gateway использует Keycloak только как auth provider: login, refresh, logout, token validation.

Конфигурация самого Keycloak лежит в:

```text
../auth/keycloak/
```

API управления Keycloak лучше добавлять отдельным admin-модулем позже:

```text
app/api/routers/keycloak_admin.py
infrastructure/auth/keycloak_admin_client.py
```

Так пользовательская авторизация не смешивается с операциями управления realm/users/roles.

## Локальный Запуск

```bash
uv sync
PYTHONPATH=src uv run python src/app/run.py
```

В `API_MODE=DEV` Gateway не проверяет токены Keycloak и использует локального пользователя:

```text
id=dev-user
roles=admin,vn1-user
```

Auth endpoints `/auth/login`, `/auth/token` и `/auth/refresh` в этом режиме не обращаются в Keycloak.

В `PROD` авторизация обязательна: Gateway проверяет токен и наличие ролей из `AUTH_REQUIRED_ROLES`, по умолчанию `vn1-user`.

## Docker

Gateway поднимается compose-файлом своего слоя:

```bash
make up SERVICE=api-gateway
```

В полном стенде этот файл подключается вместе с root proxy, auth, frontend, generator и skills.

## Make

```bash
make dev
make prod
make test
make logs
make restart
```

## Errors

HTTP-ошибки и SSE-протокол skills описаны в `../docs/ERROR_PROTOCOL.md`.

Gateway работает как `chat-service`: промежуточные SSE-события skill пропускает наружу, терминальный `data.status=success|error` с `fragments` перехватывает и заменяет финальным `event: set` с message payload.

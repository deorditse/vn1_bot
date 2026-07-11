# frontend

Текущий frontend-проект на Vite, React и TypeScript.

## Ответственность

Код frontend находится в `src/`.

- UI приложения;
- авторизация пользователя;
- формы и страницы текущего сценария;
- авторизация через `/auth`;
- вызовы backend API через `/api`;
- в будущем: чат, история, SSE-прогресс, отображение использованных skills и подтверждающих источников.

## Текущая Интеграция

Сейчас frontend работает с публичными префиксами одного домена.

Через nginx frontend доступен на `/`, auth API проксируется через `/auth` в `auth-service`, generator API через `/generator-api` в `backend-vn1`, а остальные backend API через `/api` в `api-gateway`.

Gateway сам решает, куда отправить запрос дальше:

```text
frontend -> /auth -> auth-service -> Keycloak
frontend -> /generator-api -> generator
frontend -> /api -> api-gateway -> skills | other backend logic
```

Прямых вызовов skills из frontend быть не должно.

## Команды

```bash
make run
make run-prod
make prod
make test
make restart
make stop
```

Dev proxy:

```text
/api  -> http://localhost:8000
/generator-api -> http://localhost:8010
/auth -> http://localhost:8030/v1/auth
```

## Deployment

Dockerfile frontend лежит здесь, но nginx-конфиг для образа вынесен в:

```text
../shared/ci-cd/frontend/nginx-default.conf
```

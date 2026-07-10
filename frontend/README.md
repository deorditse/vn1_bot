# frontend

Текущий frontend-проект на Vite, React и TypeScript.

## Ответственность

- UI приложения;
- авторизация пользователя;
- формы и страницы текущего generator-сценария;
- вызовы backend API через `/api`;
- в будущем: чат, история, SSE-прогресс, отображение использованных skills и подтверждающих источников.

## Текущая Интеграция

Сейчас frontend работает с backend-сервисом `generator`, который в `docker-compose.yml` называется `backend-vn1`.

Через nginx frontend доступен на `/`, а backend API проксируется через `/api`.

## Будущая Интеграция

После появления `api-gateway` frontend должен ходить только в Gateway:

```text
frontend -> /api -> api-gateway -> skills
```

Прямых вызовов skills из frontend быть не должно.

## Команды

```bash
npm install
npm run dev
npm run build
```

## Deployment

Dockerfile frontend лежит здесь, но nginx-конфиг для образа вынесен в:

```text
../shared/ci-cd/frontend/nginx-default.conf
```

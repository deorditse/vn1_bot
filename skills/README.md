# skills

Папка для независимых сервисов-навыков.

Каждый skill должен быть отдельным сервисом и реализовывать общий HTTP/SSE-протокол, который вызывает `api-gateway`.
Код каждого Python skill должен находиться в `src/`.
Межсервисный user/security context передается только через `Authorization: Bearer <access_token>`.

## Общий Принцип

Skill отвечает только за свой источник данных:

- принимает запрос от Gateway;
- ищет информацию в своем источнике;
- стримит события прогресса;
- возвращает найденные источники;
- возвращает результат или отказ, если подтвержденных источников нет.

## Планируемые Skills

- `product-kb-skill` - внутренняя база знаний продукта.
- `gitlab-skill` - GitLab issues, merge requests, код, README и обсуждения.
- `wiki-skill` - wiki/Confluence/Notion, требования, регламенты и FAQ.
- `figma-skill` - Figma-макеты, экраны, компоненты и UX-решения.
- `support-skill` - обращения пользователей, тикеты, инциденты.

## Docker

Общий compose-фрагмент skills:

```text
skills/docker-compose.yaml
```

Каждый skill должен иметь свой `Dockerfile`, а при необходимости и свой compose-фрагмент:

```text
skills/<skill-name>/Dockerfile
skills/<skill-name>/docker-compose.yaml
```

Файл `skills/docker-compose.yaml` собирает включенные skills через `extends`.
Корневой `docker-compose.yml` их не описывает: он остается только для nginx/proxy.

Полный стенд подключает skills через корневой `Makefile`.

Один skill можно перезапустить отдельно:

```bash
make restart SERVICE=gitlab-skill
```

Чтобы добавить новый skill:

1. создать `skills/<skill-name>/Dockerfile`;
2. создать `skills/<skill-name>/docker-compose.yaml`;
3. добавить сервис в `skills/docker-compose.yaml`;
4. добавить enum/config в `api-gateway`.

## Контракт

Контракт будет общим для всех skills:

```text
GET  /manifest
POST /v1/run/stream
```

SSE-события должны позволять Gateway показывать frontend ход работы: какой skill используется, что ищется, какие источники найдены и почему сформирован или отклонен ответ.

# Project Rules

## 1. Стек И Команды

- Skill layer состоит из независимых HTTP/SSE сервисов в `skills/<skill-name>`.
- Общий contract для включенного skill: `GET /manifest`, `POST /v1/run/stream`.
- Gateway вызывает skills через HTTP/SSE, не через Python imports.
- Перезапуск включенного skill: `make restart SERVICE=<skill-name>` из корня.
- Compose entrypoint: `skills/docker-compose.yaml`.

## 2. Конвенции

- Каждый Python skill держит runtime-код в `src/`, настройки в `src/common/config/settings`.
- Каждый skill имеет собственные `docs/specs` и `docs/rules.md`.
- Skill отвечает только за свой источник данных.
- Промежуточный прогресс стримится SSE fragments, финал отдается terminal payload.
- User/security context передается через `Authorization: Bearer <access_token>`.
- Potential reusable capabilities описываются в `skills/docs/skills`.

## 3. Инварианты

- Skills не импортируют `api-gateway`, `generator`, sibling skills или monorepo root как Python packages.
- Все skills соблюдают `../shared/docs/protocol/sse-stream.md` и `../shared/docs/protocol/error-protocol.md`.
- Skill не выдумывает источники и должен уметь отказать, если подтвержденных данных нет.
- Secrets внешних систем не попадают в ответы, логи и examples.
- Новый skill не считается подключенным, пока не обновлены compose, gateway enum/config/routing и docs.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый skill: `skills/<skill-name>/Dockerfile`, `docker-compose.yaml`, `src/`, `docs/specs`, `docs/rules.md` из `shared/templates/sdd/rules.md`.
- Новый source connector: settings/env + infrastructure adapter + spec с permissions.
- Новый event type: сначала обновить `shared/docs/protocol/sse-stream.md`, затем gateway/frontend consumers.
- Новый skill candidate: документ в `skills/docs/skills/<capability>.md`.

## 5. Что Не Автоматизировать Без Согласования

- Создание production-ready skill без manifest, stream endpoint и gateway integration.
- Подключение внешнего SaaS/API с production credentials.
- Изменение общего SSE protocol ради одного skill.
- Автоматические destructive actions во внешних системах.

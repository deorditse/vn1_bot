# Project Rules

## 1. Стек И Команды

- Planned Python/FastAPI skill service.
- Перед реализацией зафиксировать runtime stack, dependency manager и quality gate в этом файле.
- Ожидаемый общий contract: `GET /manifest`, `POST /v1/run/stream`.
- Container integration должна проходить через `skills/docker-compose.yaml`.

## 2. Конвенции

- Runtime-код будущего сервиса держать в `src/`.
- Wiki connectors, page filters и index settings описывать в settings/env.
- Ответы должны ссылаться на конкретные wiki pages/documents, если они доступны.
- Retrieval, индексацию и ranking rules фиксировать в spec.

## 3. Инварианты

- SSE и error contracts берутся из `../../../shared/docs/protocol`.
- Закрытые wiki-разделы нельзя раскрывать пользователю без подтвержденного доступа.
- Wiki-ответы нельзя смешивать с GitLab code search без routing решения gateway.
- При неуверенности skill задает уточнение или отдает релевантные источники без финального утверждения.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/wiki-skill/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/wiki-skill/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/wiki-skill/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый wiki provider: spec + connector + auth/permissions model.
- Новый page type/index: schema + retrieval examples.
- Новый answer mode: prompt/template + acceptance examples.
- Новый cache/index storage: invalidation и reindex runbook.

## 5. Что Не Автоматизировать Без Согласования

- Bulk export закрытых wiki spaces.
- Подключение нового SaaS provider с production credentials.
- Изменение permissions model.
- Автообновление или запись страниц wiki.

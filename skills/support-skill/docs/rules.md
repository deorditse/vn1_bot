# Project Rules

## 1. Стек И Команды

- Planned Python/FastAPI skill service.
- Перед реализацией зафиксировать runtime stack, dependency manager и quality gate в этом файле.
- Ожидаемый общий contract: `GET /manifest`, `POST /v1/run/stream`.
- Container integration должна проходить через `skills/docker-compose.yaml`.

## 2. Конвенции

- Runtime-код будущего сервиса держать в `src/`.
- Ticket/CRM/chat sources подключать только через settings/env.
- Ответы должны разделять найденные факты, предложенные действия и открытые вопросы.
- Для workflow фиксировать permissions, audit trail и fallback в spec.

## 3. Инварианты

- SSE и error contracts берутся из `../../../shared/docs/protocol`.
- Персональные данные раскрываются только в минимальном объеме, нужном для запроса.
- Destructive actions запрещены без отдельного подтверждения.
- Source access должен учитывать user/security context от gateway.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/support-skill/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/support-skill/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/support-skill/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый support provider: spec + connector + permissions/audit model.
- Новый action: dry-run mode + explicit confirmation + audit event.
- Новый classification workflow: prompt/template + evaluation examples.
- Новый escalation path: config + runbook.

## 5. Что Не Автоматизировать Без Согласования

- Закрытие тикетов, отправку сообщений пользователям или изменение статусов.
- Подключение production CRM/helpdesk credentials.
- Bulk export обращений пользователей.
- Сохранение PII вне approved storage.

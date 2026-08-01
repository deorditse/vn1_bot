# Project Rules

## 1. Стек И Команды

- Planned Python/FastAPI skill service.
- Перед реализацией зафиксировать runtime stack, dependency manager и quality gate в этом файле.
- Ожидаемый общий contract: `GET /manifest`, `POST /v1/run/stream`.
- Container integration должна проходить через `skills/docker-compose.yaml`.

## 2. Конвенции

- Runtime-код будущего сервиса держать в `src/`.
- Figma files, pages и node ids описывать через settings/env и spec.
- Ответы должны ссылаться на конкретные Figma file/node identifiers, если они доступны.
- Raw Figma payload сохранять только при явном storage decision.

## 3. Инварианты

- SSE и error contracts берутся из `../../../shared/docs/protocol`.
- Figma tokens и private file links не попадают в логи и ответы сверх необходимого source reference.
- При недоступном файле возвращается нормализованная ошибка с причиной.
- Frontend-код по макету не генерируется без отдельного explicit request/spec.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/figma-skill/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/figma-skill/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/figma-skill/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый Figma connector scope: spec + env/settings + permissions notes.
- Новый extraction mode: nodes/components/styles contract + examples.
- Новый visual summary format: prompt/template + expected output.
- Новый cache: TTL, invalidation и storage policy.

## 5. Что Не Автоматизировать Без Согласования

- Подключение production Figma token.
- Скачивание или сохранение полного design file без retention decision.
- Массовую генерацию frontend-кода из Figma.
- Изменение permissions/scopes Figma integration.

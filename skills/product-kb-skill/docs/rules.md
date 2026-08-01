# Project Rules

## 1. Стек И Команды

- Planned Python/FastAPI skill service.
- Перед реализацией зафиксировать runtime stack, dependency manager и quality gate в этом файле.
- Ожидаемый общий contract: `GET /manifest`, `POST /v1/run/stream`.
- Container integration должна проходить через `skills/docker-compose.yaml`.

## 2. Конвенции

- Runtime-код будущего сервиса держать в `src/`.
- Product knowledge sources, indexes и retrieval settings описывать в settings/env.
- Каждый ответ должен отделять подтвержденные факты, найденные источники и предположения.
- Если данных недостаточно, skill возвращает уточнение или отказ, а не уверенный ответ.

## 3. Инварианты

- SSE и error contracts берутся из `../../../shared/docs/protocol`.
- Приватные документы и пользовательский контент нельзя сохранять вне approved storage.
- Knowledge source access должен учитывать права пользователя из gateway context.
- Источники знаний нельзя хардкодить в workflow nodes.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `skills/product-kb-skill/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `skills/product-kb-skill/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `skills/product-kb-skill/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новый source: spec + settings/env + adapter + permissions model.
- Новый retrieval mode: spec с ranking rules, fallback и acceptance examples.
- Новый index/storage: migration/operations notes + deletion policy.
- Новый answer format: prompt/template change + examples.

## 5. Что Не Автоматизировать Без Согласования

- Подключение production knowledge base.
- Bulk indexing приватных документов.
- Изменение retention policy.
- Ответы без ссылок на подтвержденные источники для factual requests.

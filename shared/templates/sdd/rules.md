# Project Rules

## 1. Стек И Команды

- <runtime stack, language versions, frameworks>
- <dependency manager and lockfile>
- Dev run: `<command>`
- Quality gate: `<command>`
- Service restart/deploy: `<command>`

## 2. Конвенции

- <project structure rule>
- <naming/import rule>
- <configuration/settings rule>
- <logging/error handling rule>
- <testing/documentation rule>

## 3. Инварианты

- <contract or architecture rule that must not be broken casually>
- <security/privacy rule>
- <cross-service boundary rule>
- <public API compatibility rule>
- <data retention or storage rule>

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `docs/specs/done/<feature-name>/spec.md`.
- Новый endpoint/feature/module: <where to add code, schema, tests>.
- Новый integration/provider: <where settings, adapter, docs live>.
- Новый contract/prompt/workflow: <required files and checks>.

## 5. Что Не Автоматизировать Без Согласования

- <dependency/tooling changes>
- <security/auth/session changes>
- <public contract breaking changes>
- <production data or credentials actions>
- <destructive external-system actions>

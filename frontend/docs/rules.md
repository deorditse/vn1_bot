# Project Rules

## 1. Стек И Команды

- React 19, TypeScript 5, Vite 7, React Router 7.
- State/API: Redux Toolkit и RTK Query.
- UI: Ant Design 6, `lucide-react`, Less/CSS Modules.
- Менеджер пакетов: npm, lockfile `package-lock.json`.
- Dev: `npm run dev`.
- Проверка production build: `npm run build`.
- Preview build: `npm run preview`.

## 2. Конвенции

- Слои: `src/app`, `src/pages`, `src/widgets`, `src/features`, `src/entities`, `src/shared`.
- Импорты идут сверху вниз: `app -> pages -> widgets -> features -> entities -> shared`.
- API-типы держать рядом с API-клиентом: `api/types.ts`, `model/types.ts`, public exports через `index.ts`.
- Server state вести через существующий RTK Query/API layer; локальный UI state держать в компоненте или feature model.
- Стили компонента держать рядом с компонентом. Постоянный UI не оформлять inline styles.
- Иконки брать из `lucide-react`, если подходящая иконка есть в библиотеке.

## 3. Инварианты

- Frontend не содержит backend business logic и не импортирует код сервисов из `generator`, `auth`, `api-gateway`, `skills`.
- Auth source of truth один: gateway/auth cookies и `/me`/context flow; токены не хранить в localStorage.
- В UI не показывать raw backend exception, stack trace, provider payload или секреты.
- Публичные routes и guards менять только вместе с проверкой auth-flow.
- API base URLs брать из env/config, не хардкодить hostnames в компонентах.
- Пользовательские flows перед реализацией описывать в `frontend/docs/specs/todo/<feature-name>/spec.md`.

## 4. Точки Расширения

- Перед началом задачи читать активный spec из `frontend/docs/specs/todo/<feature-name>/spec.md`; шаблон брать из `shared/templates/sdd/spec.md`.
- После приемки переносить spec в `frontend/docs/specs/done/<feature-name>/spec.md`.
- Архитектурные решения фиксировать в `frontend/docs/adr/ADR-<number>-<slug>.md`; шаблон брать из `shared/templates/sdd/adr.md`.
- Новая страница: `src/pages/<page>/` + route config + нужные widgets/features.
- Новый API endpoint: request/response types + query/mutation в существующем API layer + UI states loading/error/empty/success.
- Новый persistent UI preference: явно выбрать `localStorage` или `sessionStorage`, описать ключ и fallback.
- Новый shared UI primitive: `src/shared/ui/`, если компонент используется минимум двумя независимыми местами.
- Новый сценарий генерации/загрузки: spec в `frontend/docs/specs/todo/<feature-name>/spec.md` + контракт с `generator` или `api-gateway`.

## 5. Что Не Автоматизировать Без Согласования

- Установку новых UI kits, state managers, routers или form libraries.
- Изменение auth storage model, route guards и cookie/session behavior.
- Массовый перенос слоев или переименование public API exports.
- Изменение build tooling, Dockerfile, nginx routing или env variable names.

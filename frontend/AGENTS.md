# Frontend Architecture Notes

Документ для агента, который проектирует или продолжает frontend-разработку. Описание намеренно общее: его можно применять к разным продуктовым web-приложениям, адаптируя детали под конкретный репозиторий.

## Цель Архитектуры

Frontend должен быть предсказуемым, расширяемым и удобным для сопровождения. Основные приоритеты:

- понятное разделение ответственности между слоями;
- минимальная связность между фичами;
- единый подход к API, состоянию, маршрутизации и UI;
- простое добавление новых страниц и сценариев;
- строгая типизация контрактов;
- воспроизводимый build и понятный quality gate.

## Рекомендуемый Стек

Базовый стек для современного SPA:

- React + TypeScript.
- Vite или аналогичный быстрый bundler.
- React Router для маршрутизации.
- Redux Toolkit + RTK Query или TanStack Query для server state.
- Локальный state через React hooks.
- UI kit: Ant Design, MUI, Mantine или собственная design system.
- CSS Modules, Less/Sass Modules, vanilla-extract, Tailwind или другой единый styling-подход.
- Иконки из одной библиотеки, например lucide-react.
- ESLint, TypeScript strict mode, formatter.

Выбор конкретных библиотек должен быть единым по проекту. Не стоит смешивать несколько UI kits, несколько API-клиентов и несколько конкурирующих state-management подходов без сильной причины.

## Слои Приложения

Удобная базовая структура:

```text
src/
  app/
  pages/
  widgets/
  features/
  entities/
  shared/
```

Назначение слоев:

- `app` - инициализация приложения, providers, routing, store, layout, глобальные стили.
- `pages` - route-level экраны, которые собирают сценарий из фич, виджетов и shared-компонентов.
- `widgets` - крупные композиционные блоки интерфейса: header, sidebar, dashboard panel, workspace.
- `features` - пользовательские действия и бизнес-сценарии: auth, upload, search, filters, editing.
- `entities` - доменные сущности и их представление: user, product, document, order.
- `shared` - инфраструктура и переиспользуемые primitives: api client, ui kit wrappers, lib, config, assets, types.

Если проект небольшой, слой `entities` можно не вводить сразу. Лучше иметь меньше слоев, чем искусственно разносить код.

## Правила Зависимостей

Слои должны зависеть сверху вниз:

```text
app -> pages -> widgets -> features -> entities -> shared
```

Общие правила:

- `shared` не должен импортировать код из верхних слоев.
- `features` не должны напрямую зависеть от `pages`.
- `pages` могут собирать разные фичи вместе.
- Публичные экспорты каждого slice держать в `index.ts`.
- Не импортировать глубоко из чужого slice, если есть public API.
- Межслойные импорты делать через алиасы, например `@shared/*`, `@features/*`, `@pages/*`.

## Структура Фичи Или Страницы

Рекомендуемый шаблон:

```text
feature-or-page/
  api/
    index.ts
    types.ts
  model/
    hooks.ts
    types.ts
    selectors.ts
    slice.ts
  lib/
    helpers.ts
  ui/
    Component/
      Component.tsx
      Component.module.css
      index.ts
  index.ts
```

Используйте только те папки, которые реально нужны. Если у фичи нет API или model-логики, не создавайте пустые директории.

## Routing

Маршруты лучше держать в централизованной конфигурации:

- path;
- element;
- auth/role restrictions;
- layout;
- nav metadata;
- lazy loading.

Новые страницы добавлять через конфиг маршрутов, а не размазывать route-логику по приложению. Защищенные маршруты должны проходить через единый guard, например `RequireAuth`.

## State Management

Разделяйте типы состояния:

- Server state: данные с backend, кеш, refetch, invalidation.
- Client state: локальный UI state, выбранные tab/filter/modal, drag state.
- Form state: значения и ошибки формы.
- Global app state: auth, theme, layout preferences, feature flags.

Рекомендации:

- Для server state использовать RTK Query или TanStack Query.
- Для простого UI state использовать `useState`, `useReducer`, `useMemo`.
- Не класть все подряд в Redux.
- Глобальный store использовать только для данных, которые реально нужны нескольким независимым частям приложения.
- Persist в localStorage/sessionStorage применять выборочно: пользовательские настройки, draft values, feature preferences.
- Не хранить чувствительные данные в localStorage.

## API Подход

Должна быть единая точка настройки API:

- base URL;
- headers;
- credentials;
- refresh token/session handling;
- error normalization;
- retry policy;
- cancellation;
- logging в dev mode.

Контракты должны быть типизированы:

- отдельные `Request`/`Response` типы;
- нормализация backend DTO при необходимости;
- явная обработка nullable/optional полей;
- пользовательские ошибки не должны показывать raw backend exception.

При добавлении endpoint:

1. Описать request/response types.
2. Добавить query/mutation в общий API layer.
3. Указать cache tags/invalidation, если используется кеш.
4. Обработать loading/error/empty/success состояния в UI.

## Auth

Auth должен иметь единый provider или app-level модуль:

- загрузка текущего пользователя при старте;
- login/logout;
- refresh session/token;
- обработка `401`;
- redirect на login;
- проверка ролей и прав;
- dev bypass, если он нужен команде.

Источник истины для auth должен быть один. Например:

- secure httpOnly cookie + `/me`;
- или access token в памяти + refresh flow;
- или внешний identity provider.

Не смешивайте несколько независимых способов определения авторизации.

## UI И Design System

Интерфейс должен строиться на едином визуальном языке:

- design tokens: colors, spacing, radius, shadows, typography;
- базовые primitives: Button, Input, Select, Modal, Card, Flex, Stack, Skeleton;
- единые состояния: loading, empty, error, disabled, success;
- единые правила responsive layout.

Практические правила:

- Использовать UI kit или shared-компоненты, а не создавать каждый control заново.
- Стили компонента держать рядом с компонентом.
- Не использовать inline styles для постоянного UI.
- Не добавлять новый визуальный паттерн, если уже есть похожий.
- Иконки брать из одной библиотеки.
- Формы должны иметь валидацию, понятные ошибки и disabled/loading states.
- Все интерактивные элементы должны быть доступны с клавиатуры.

## Styling

Выберите один основной подход:

- CSS Modules;
- Sass/Less Modules;
- Tailwind;
- CSS-in-JS;
- design-system tokens.

Важно:

- глобальные стили держать минимальными;
- не завязывать компоненты на случайные глобальные классы;
- использовать CSS variables или theme tokens для цветов и spacing;
- избегать magic numbers без причины;
- проверять layout на mobile, tablet и desktop.

## Forms

Для сложных форм используйте единый подход:

- controlled или form library, например React Hook Form;
- schema validation, например Zod/Yup, если много правил;
- server-side errors мапить на поля;
- submit должен иметь loading state;
- ошибки должны быть понятны пользователю;
- reset и dirty state должны быть предсказуемыми.

## Асинхронные Сценарии

Каждый async workflow должен явно покрывать состояния:

- initial;
- loading;
- success;
- empty;
- error;
- retry;
- partial success, если возможно.

Не прячьте ошибки в console. Пользователь должен понимать, что произошло и что можно сделать дальше.

## Code Splitting

Lazy loading стоит применять для:

- route-level страниц;
- тяжелых виджетов;
- редакторов, charts, markdown/rendering tools;
- редко используемых модальных сценариев.

Fallback должен быть стабильным по размеру, чтобы страница не прыгала при загрузке.

## Тестирование И Quality Gate

Минимальный quality gate:

```bash
npm run typecheck
npm run lint
npm run test
npm run build
```

Если часть команд отсутствует, агент должен либо добавить их по договоренности, либо явно указать, что именно невозможно проверить.

Что покрывать тестами:

- чистые helpers;
- сложные hooks;
- критичные user flows;
- API mapping;
- permission guards;
- компоненты с нетривиальной логикой.

Для UI-регрессий полезны Playwright/Cypress smoke tests по ключевым сценариям.

## Environment И Config

Runtime/config значения должны быть централизованы:

- API base URL;
- feature flags;
- auth mode;
- external service URLs;
- build metadata.

Правила:

- не читать `import.meta.env` хаотично по всему приложению;
- иметь typed config helper;
- документировать обязательные переменные;
- не коммитить секреты.

## Добавление Новой Фичи

Порядок работы:

1. Понять user flow и backend contract.
2. Выбрать слой: page, widget, feature или entity.
3. Описать типы данных.
4. Добавить API endpoints.
5. Собрать model hook/state.
6. Реализовать UI на существующих primitives.
7. Добавить route/nav, если нужен экран.
8. Покрыть loading/error/empty/success.
9. Проверить responsive и accessibility.
10. Запустить quality gate.

## Принципы Для Агента

- Сначала читать существующие паттерны проекта.
- Не внедрять новую библиотеку, если задача решается текущим стеком.
- Держать изменения локальными по смыслу.
- Не смешивать refactoring и feature work без необходимости.
- Предпочитать типизированные контракты и явные состояния.
- Не ломать public API slice без причины.
- Если есть сомнение между быстрым локальным решением и новой абстракцией, выбирать локальное решение до появления повторения.
- После изменений обязательно сообщать, что проверено и что осталось непроверенным.

# Gateway MCP Communication With Skills

## Цель
Перевести внутреннее взаимодействие `api-gateway -> skills` с legacy HTTP/SSE вызовов на MCP, сохранив текущий внешний контракт `frontend -> api-gateway`.

Gateway должен стать MCP-клиентом для skill-сервисов: обнаруживать MCP tools/resources, вызывать выбранный skill через MCP tool и преобразовывать MCP progress/result/error в существующий frontend SSE формат.

## Контекст
Сейчас `api-gateway` работает со skill-сервисами через текущие HTTP/SSE endpoint-ы и skill metadata/config. Для новой схемы skill-сервис должен отдавать MCP endpoint `/mcp/`, resource `skill://<name>/SKILL.md` и tools через `list_tools()`.

Эталонный контракт уже есть в `native-orchestrator-main`:
- `specs/mcp-skill-contract/spec.md`
- `src/infrastructure/mcp_client/discovery.py`
- `src/infrastructure/mcp_client/registry.py`
- `src/app/services/skill_stream.py`

Целевой пример skill-сервиса для миграции: `chat-with-documents-main`, который должен быть доступен gateway как MCP skill `chat_w_doc`.

## Что делаем
- В `api-gateway` добавить MCP client adapter для skill-сервисов на базе FastMCP/MCP Python client.
- Добавить discovery MCP skill catalog:
  - читать configured MCP endpoints из settings/env;
  - вызывать `list_resources()` и искать `skill://<name>/SKILL.md`;
  - читать frontmatter `SKILL.md`: `name`, `title`, `description`, `mode`, `tool_name`, `direct_invoke`;
  - вызывать `list_tools()` и сохранять tool name, description, input schema.
- Ввести registry MCP skills:
  - один config entry gateway = один skill в registry;
  - ключ config должен совпадать с `name` в `SKILL.md`;
  - поддержать `add_orchestrator`, чтобы skill можно было скрыть из auto-routing, но оставить callable явно.
- Обновить skill selection/routing:
  - использовать MCP catalog вместо legacy manifest как основной источник skill metadata;
  - для выбранного skill загружать инструкции из `SKILL.md`;
  - для `entrypoint` skill вызывать `tool_name`;
  - для `agentic` skill открывать доступ к tools после выбора/загрузки skill.
- Реализовать сбор MCP tool arguments:
  - gateway сам инжектит `thread_id`, `message_id`, `history_messages`, `file_ids`, `user/context`, `extra_data`;
  - LLM не должна заполнять protected context fields;
  - перед `call_tool` валидировать arguments по JSON Schema tool.
- Реализовать stream adapter `MCP -> frontend SSE`:
  - MCP progress/logging events преобразовывать в текущие VN1 `think` fragments;
  - MCP structured result преобразовывать в финальный assistant terminal payload и `event: set`;
  - MCP/tool errors преобразовывать в текущий error terminal формат gateway.
- Обновить settings/config gateway:
  - добавить MCP endpoint для каждого skill, например `chat_w_doc.url = ".../mcp/"`;
  - оставить legacy URL/path как fallback или deprecated config до отдельного решения об удалении.
- Обновить документацию `shared/docs/protocol`:
  - описать внутренний контракт `api-gateway -> skills` по MCP;
  - зафиксировать endpoint, resource, tool schema, progress mapping, result mapping, error mapping.
- Добавить observability:
  - логи discovery success/error/name mismatch/schema validation error;
  - метрики MCP discovery, tool call duration, tool call result, upstream unavailable.

## Что НЕ делаем
- Не переводим frontend на MCP.
- Не меняем публичный `/chat/stream` contract gateway.
- Не меняем frontend SSE parser, terminal event и `event: set` payload.
- Не удаляем legacy HTTP/SSE skill endpoints в первой итерации.
- Не меняем бизнес-логику конкретных skills внутри gateway.
- Не добавляем write-actions во внешние системы как часть миграции транспорта.

## Критерии приёмки
- [ ] `api-gateway` умеет обнаруживать MCP skill по `skill://<name>/SKILL.md` и `list_tools()`.
- [ ] Gateway registry отклоняет skill, если config key не совпадает с `SKILL.md name`.
- [ ] Gateway валидирует MCP tool arguments по JSON Schema до вызова `call_tool`.
- [ ] Gateway сам инжектит dialog/user context в invoke-style tools.
- [ ] `/chat/stream` сохраняет прежний frontend SSE формат.
- [ ] MCP progress/logging events доходят до frontend как промежуточные `think` fragments.
- [ ] MCP structured result становится финальным assistant response.
- [ ] MCP/tool error становится текущим gateway error terminal response.
- [ ] `chat_w_doc` вызывается gateway через MCP endpoint `/mcp/`.
- [ ] Legacy HTTP/SSE skill вызов либо работает как fallback, либо явно помечен deprecated в документации/config.
- [ ] Покрыты сценарии: successful tool call, progress events, invalid schema args, skill name mismatch, MCP upstream unavailable, client disconnect.

## Открытые вопросы
- Используем ли FastMCP client в gateway как в `native-orchestrator-main` или официальный MCP Python SDK напрямую?
- Нужен ли автоматический fallback на legacy HTTP/SSE endpoint, если MCP endpoint skill недоступен?
- Где хранить access policy для MCP skills: в gateway config, в `SKILL.md`, или в обоих местах?
- Передаём ли весь user/security context в tool arguments или только минимальный набор полей?
- Должен ли gateway поддержать `agentic` multi-tool skills в первой итерации или сначала только `entrypoint` tools?

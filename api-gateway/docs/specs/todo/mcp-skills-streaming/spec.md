# MCP Streaming Between Gateway And Skills

## Цель
Перевести внутреннее взаимодействие `api-gateway -> skills` на MCP, сохранив текущий SSE-контракт `frontend -> api-gateway`. Gateway должен выступать адаптером: получать MCP progress/result от skills и отдавать frontend прежние VN1 SSE events.

## Контекст
Текущий frontend stream contract описан в `shared/docs/protocol/sse-stream.md`: frontend получает промежуточные `data.data.fragment_type` events и финальный `event: set`.

Сейчас `api-gateway` вызывает skills как HTTP/SSE upstream через `GET /manifest` и `POST /v1/run/stream`; основная реализация находится в `api-gateway/src/app/use_cases/stream_skill.py` и `api-gateway/src/infrastructure/clients/skill_client.py`.

Первый рабочий skill - `skills/gitlab-skill`, который сейчас реализует FastAPI endpoint `/v1/run/stream` и возвращает VN1 terminal payload. Для новой архитектуры skill должен получить MCP endpoint и MCP tools, а gateway должен заменить прямой SSE-proxy на MCP client adapter.

## Что делаем
- В `shared/docs/protocol` добавить документ `mcp-skills.md` с контрактом `api-gateway -> skills`: transport, endpoint, tool naming, auth/context, progress/result/error mapping.
- В `api-gateway` добавить MCP client adapter для skills вместо прямого upstream SSE proxy на границе `gateway -> skill`.
- В `api-gateway` сохранить внешний endpoint `/chat/stream` и текущий frontend SSE wire format без breaking changes.
- В `api-gateway` преобразовывать MCP progress notifications в VN1 `think` fragments для frontend.
- В `api-gateway` преобразовывать MCP tool result в финальный assistant message `event: set`.
- В `api-gateway` преобразовывать MCP/tool errors в текущий VN1 error terminal/final event.
- В skill config gateway добавить MCP endpoint и tool metadata вместо `stream_path` как основного способа вызова skill.
- В `skills/gitlab-skill` добавить MCP server/tool, эквивалентный текущему GitLab search/answer workflow.
- В `skills/gitlab-skill` обеспечить передачу `request_id`, `thread_id`, `message_id`, `user_id`, `message` и дополнительного context через MCP tool arguments.
- В `skills/gitlab-skill` передавать progress выполнения через MCP progress notifications или выбранный FastMCP progress mechanism.
- В `skills/docs/rules.md` обновить описание skill layer: внешний frontend SSE остается за gateway, внутренняя связь gateway-skills идет через MCP.

## Что НЕ делаем
- Не переводим frontend на MCP.
- Не меняем frontend SSE parser и UI contract.
- Не меняем публичный `/chat/stream` contract gateway.
- Не удаляем legacy `GET /manifest` и `POST /v1/run/stream` до отдельного ADR/migration decision.
- Не делаем token-by-token streaming финального ответа в первой версии, если выбранный MCP/FastMCP transport не дает стабильный стандартный механизм.
- Не добавляем write-actions в GitLab или другие внешние системы.
- Не меняем LLM routing semantics orchestrator, кроме способа вызова выбранного skill.

## Критерии приёмки
- [ ] Frontend продолжает получать промежуточные progress events и финальный `event: set` в прежнем формате.
- [ ] `api-gateway` вызывает `gitlab-skill` через MCP, а не через основной `POST /v1/run/stream` flow.
- [ ] MCP progress из `gitlab-skill` отображается во frontend как VN1 `think` fragments.
- [ ] MCP tool result из `gitlab-skill` преобразуется gateway в финальный assistant message.
- [ ] MCP/tool error преобразуется gateway в текущий error response для frontend.
- [ ] User/security context передается от gateway до MCP skill.
- [ ] `shared/docs/protocol/mcp-skills.md` описывает endpoint, tool input/output, progress mapping и error mapping.
- [ ] Legacy HTTP/SSE skill endpoints либо сохранены как fallback, либо явно помечены deprecated в документации.
- [ ] Проверены сценарии: success, no sources, invalid tool input, MCP upstream unavailable, client disconnect.

## Открытые вопросы
- Какой Python client использовать в gateway: FastMCP client или официальный MCP Python SDK?
- Какой transport выбираем как основной: MCP Streamable HTTP или legacy MCP SSE?
- Нужен ли fallback gateway на legacy `/v1/run/stream`, если MCP endpoint skill недоступен?
- Должен ли каждый skill иметь один универсальный MCP tool или несколько domain-specific tools?
- Каким форматом MCP tool result должен возвращать sources, processing fragments и финальный текст?

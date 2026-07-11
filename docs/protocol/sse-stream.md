# SSE Stream Protocol

This protocol follows the same shape as `Sber/backend/chat-service`.

## Transport

SSE responses use:

```http
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

## Intermediate Events

Skill services send intermediate progress events as `data.data` fragments.

```text
data: {"data":{"fragment_id":1,"fragment_type":"think","status":"in_progress","streaming":false,"content":"### Ищу...","token_usage":null,"duration_s":null}}
data: {"data":{"fragment_id":1,"fragment_type":"think","status":"success","streaming":false,"content":"### Найдено","token_usage":123,"duration_s":1.2}}
```

`api-gateway` passes intermediate events through unchanged.

## Terminal Event

Skill services must finish the stream with a terminal `data.data` payload.

```text
data: {"data":{"status":"success","fragments":[{"fragment_id":2,"fragment_type":"response","status":"success","streaming":false,"content":"Ответ"}]}}
```

Error terminal payload uses the same shape:

```text
data: {"data":{"status":"error","fragments":[{"fragment_type":"response","status":"error","content":"Не удалось обработать запрос."}]}}
```

`api-gateway` consumes the terminal event and does not forward it as-is.

## Gateway Final Event

After receiving the terminal payload, `api-gateway` emits the final frontend message with `event: set`.

```text
event: set
data: {"chat_id":"...","message_id":"...","sender":"assistant","data":"Ответ","skill":"gitlab","processing_data":{"status":"success","fragments":[]},"status":"success"}
```

Frontend should:

- render intermediate `data.data.fragment_type=think` events in thinking/status UI;
- stream intermediate `data.data.fragment_type=response` chunks as assistant response content if present;
- treat `event: set` as the final normalized message;
- store/display execution details from `processing_data.fragments`.


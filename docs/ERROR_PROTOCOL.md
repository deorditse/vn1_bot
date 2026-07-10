# Error Protocol

Все HTTP-сервисы возвращают ошибки в одном JSON-формате.

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  },
  "request": {
    "id": "request-id",
    "method": "POST",
    "path": "/chat/stream"
  },
  "service": "api-gateway",
  "status": 422
}
```

Поля:

- `success` - всегда `false` для ошибки.
- `error.code` - стабильный машинный код ошибки.
- `error.message` - короткое человекочитаемое описание.
- `error.details` - детали для UI/debug, может быть `null`.
- `request.id` - `X-Request-Id` из запроса или сгенерированный id.
- `request.method` - HTTP method.
- `request.path` - path запроса.
- `service` - сервис, который сформировал ошибку.
- `status` - HTTP status code.

В `API_MODE=DEV` unexpected errors могут содержать `error.trace`. В `PROD` traceback не возвращается.

Для SSE skills используется тот же подход, что в `chat-service`:

Промежуточные события от skill проходят как есть:

```text
data: {"data":{"fragment_type":"search","status":"success","content":"Ищем..."}}
```

Терминальный payload от skill:

```text
data: {"data":{"status":"success","fragments":[{"fragment_type":"response","status":"success","content":"Ответ"}]}}
```

Gateway перехватывает терминальный payload и вместо него отправляет финальное message-событие:

```text
event: set
data: {"chat_id":"...","message_id":"...","sender":"assistant","data":"Ответ","skill":"gitlab","processing_data":{"status":"success","fragments":[]},"status":"success"}
```

Для SSE ошибок upstream используется терминальный error payload:

```text
data: {"data":{"status":"error","fragments":[{"fragment_type":"response","status":"error","content":"Не удалось обработать запрос."}]}}
```

Frontend должен:

- показывать промежуточные `data.data.fragment_type`;
- ждать финальное `event: set`;
- брать финальный текст из `data.data`;
- хранить/показывать ход работы из `data.processing_data`.

# docs

Общая документация монорепозитория.

- `ERROR_PROTOCOL.md` - единый формат ошибок HTTP/SSE для frontend и внешних клиентов.
- `protocol/sse-stream.md` - межсервисный SSE stream protocol для api-gateway и skills.

## Как обновить и переподнять сервер

Команды ниже выполняются на сервере из корня репозитория `vn1_bot`.

### 1. Забрать свежий код

```bash
cd /path/to/vn1_bot
git pull
```

Если на сервере есть незакоммиченные локальные изменения, сначала проверь их:

```bash
git status
```

### 2. Проверить docker-compose конфигурацию

```bash
make test
```

### 3. Пересобрать и перезапустить нужные сервисы

После изменений в generator/backend:

```bash
make restart SERVICE=backend-vn1
```

После изменений во frontend:

```bash
make restart SERVICE=frontend
```

После изменений в api-gateway:

```bash
make restart SERVICE=api-gateway
```

Если менялись связи между сервисами или нужно гарантированно переподнять всё приложение:

```bash
make restart
```

`make restart` использует `docker compose up -d --build --force-recreate`, поэтому контейнеры будут пересозданы из актуального кода.

Для полного запуска можно использовать одну из команд:

```bash
make run
```

или:

```bash
make prod
```

или явную алиас-цель:

```bash
make run-prod
```

Команда `make run prod` тоже отработает через цель `prod`, но `make run-prod` читается однозначнее.

### 4. Проверить статус контейнеров

```bash
docker compose \
  -f docker-compose.yml \
  -f shared/docker-compose.yaml \
  -f auth/docker-compose.yaml \
  -f frontend/docker-compose.yaml \
  -f generator/docker-compose.yaml \
  -f skills/docker-compose.yaml \
  -f api-gateway/docker-compose.yaml \
  ps
```

### 5. Посмотреть логи после рестарта

Generator:

```bash
docker logs -f backend-vn1
```

Frontend:

```bash
docker logs -f frontend
```

API gateway:

```bash
docker logs -f api-gateway
```

Nginx:

```bash
docker logs -f nginx
```

### Быстрый сценарий для текущего изменения

Для изменений в генерации AI-описаний и frontend-интерфейсе обычно достаточно:

```bash
cd /path/to/vn1_bot
git pull
make test
make restart SERVICE=backend-vn1
make restart SERVICE=frontend
```

Если после этого запросы через `/api/generator/...` всё ещё идут в старую версию, перезапусти gateway и nginx:

```bash
make restart SERVICE=api-gateway
make restart SERVICE=nginx
```

### Ошибка `COPY ... not found` при сборке

Если Docker падает на шагах вроде:

```text
COPY generator/src ./src
COPY skills/orchestrator-skill/src ./src
failed to calculate checksum ... not found
```

значит нужные файлы не попали в Docker build context. Проверь, что на сервере есть свежая версия `.dockerignore`:

```bash
git pull
git status --short .dockerignore generator/src skills/orchestrator-skill/src
```

После обновления `.dockerignore` пересобери сервисы:

```bash
make restart SERVICE=backend-vn1
make restart SERVICE=orchestrator-skill
```

### Ошибка `404 Not Found nginx/1.27.x`

Если главная страница открывается, но прямой переход на `/instruction`, `/knowledge-base` или обновление страницы внутри приложения отдаёт:

```text
404 Not Found
nginx/1.27.x
```

это означает, что nginx не отдал React SPA fallback на `index.html`. После обновления корневого `nginx.conf` пересобери и перезапусти nginx:

```bash
git pull
make restart SERVICE=nginx
```
Если frontend-контейнер тоже был пересобран из старого образа, перезапусти frontend:

```bash
make restart SERVICE=frontend
```

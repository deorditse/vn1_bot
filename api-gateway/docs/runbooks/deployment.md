# Deployment Runbook

Команды выполняются на сервере из корня репозитория `vn1_bot`.

## Обновление Кода

```bash
cd /path/to/vn1_bot
git pull
git status
```

## Проверка Compose

```bash
make test
```

## Рестарт Сервисов

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

Для полного запуска:

```bash
make run
make prod
make run-prod
```

## Проверка Статуса

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

## Логи

```bash
docker logs -f backend-vn1
docker logs -f frontend
docker logs -f api-gateway
docker logs -f nginx
```

Если compose использует имена вида `<project>-<service>-1`, смотри точные имена через:

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

## Частые Ошибки

Если Docker падает на `COPY ... not found`, проверь, что нужные файлы попали в Docker build context и что на сервере актуальная `.dockerignore`:

```bash
git pull
git status --short .dockerignore generator/src skills/gitlab-skill/src
```

После обновления `.dockerignore` пересобери сервисы:

```bash
make restart SERVICE=backend-vn1
make restart SERVICE=gitlab-skill
```

Если прямой переход на `/instruction`, `/knowledge-base` или обновление страницы внутри SPA отдает `404 Not Found nginx`, нужен React SPA fallback на `index.html`. После обновления `nginx.conf`:

```bash
git pull
make restart SERVICE=nginx
make restart SERVICE=frontend
```

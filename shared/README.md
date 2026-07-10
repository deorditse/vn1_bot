# shared

Общая инфраструктура монорепозитория, которая не принадлежит одному конкретному сервису.

## Состав

- `certbot/` - состояние и webroot для Let's Encrypt/certbot.
- `xray-config/` - конфигурация xray, если потребуется включить proxy-контейнер.
- `ci-cd/` - общие CI/CD и deployment-конфиги.

Эти директории относятся к деплою всего стенда, поэтому они вынесены из корня, но не помещены внутрь `generator`, `frontend` или `api-gateway`.

## Использование

Пути подключаются из корневого `docker-compose.yml`:

```text
./shared/certbot/conf/
./shared/certbot/www/
./shared/xray-config/config.json
./shared/ci-cd/
```

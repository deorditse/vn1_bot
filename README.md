### Шаги для установки на сервер

## клонируем репо по SSH

ssh-keygen -t ed25519 -C "deor_dima@vn-1"
cat ~/.ssh/id_ed25519.pub
ssh -T git@github.com

## установка гита

sudo apt update
sudo apt install -y git
sudo chown -R deor_dima:deor_dima ./

git clone git@github.com:ORG/REPO.git /opt/REPO

git@github.com:deorditse/vn1_bot.git /opt/vn1_bot
## установка докер

https://docs.docker.com/engine/install/debian/

sudo apt-get update
sudo apt-get install docker-compose-plugin

sudo docker ps

### пересобрать только один, например n8n-alliance:

sudo docker compose restart n8n-vn1
sudo docker compose restart backend-vn1
sudo docker compose up -d --build n8n-vn1

### обновление завсиимостей

# 1. Обновить образ

sudo docker compose pull
sudo docker compose up -d --force-recreate
docker compose up -d --force-recreate n8n-alliance-trucks

docker image prune -f

# 2. Пересоздать контейнер с новым образом

sudo docker compose down
sudo docker compose up --build -d


docker compose up --scale backend-vn1=4
sudo docker compose up -d

## разрешения

sudo chown -R 1000:1000 ./bots/alliance_trucks/data
sudo chown -R 1000:1000 ./bots/test/data
sudo chmod -R u+rwX ./bots/alliance_trucks/data
sudo chmod -R u+rwX ./bots/test/data


###### Запуск API

```bash
uv run python3 src/app/run.py   

```

🔹 2. Удалить старые образы вручную:
sudo docker image prune -a

docker-compose down
sudo docker compose pull
docker image prune -f
docker compose up -d



## Step 3: Setting up SSL with Certbot

Certbot will obtain and install an SSL certificate from Let's Encrypt.

sudo docker compose run --rm certbot certonly \
 --webroot \
 --webroot-path /var/www/certbot/ \
 --email deor.dima@gmail.com \
 --agree-tos \
 --no-eff-email \
 -d ai-bot.vn1.ru


автопроддление 

sudo docker compose run --rm certbot renew --dry-run


Follow the on-screen instructions to complete the SSL setup.
Once completed, n8n will be accessible securely over HTTPS at your-domain.com.

IMPORTANT: Make sure you follow the above steps in order. Step 5 will modify your /etc/nginx/sites-available/n8n.conf file to something like this:
![image](https://github.com/user-attachments/assets/344187ec-5bcf-4d97-ad35-21b6562182e5)




## установка с dev зависимостяим 
uv sync --extra dev


## Авторизация через Keycloak

Keycloak поднимается отдельным контейнером и импортирует realm из `keycloak/realm-export.json`.

```bash
sudo docker compose up -d --build keycloak backend-vn1
```

Админка Keycloak:

- локально: `http://localhost:8080/keycloak`
- через nginx: `https://ai-bot.vn1.ru/keycloak`
- admin login: `${KEYCLOAK_ADMIN:-admin}`
- admin password: `${KEYCLOAK_ADMIN_PASSWORD:-admindeor}`

На сервере для корректного issuer токенов задайте:

```bash
KEYCLOAK_HOSTNAME=https://ai-bot.vn1.ru/keycloak
```

Импортированный тестовый пользователь:

- username: `vn1-user`
- password: `vn1-user`
- role: `vn1-user`

Получить access token через API:

```bash
curl -X POST 'http://localhost/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username": "vn1-user", "password": "vn1-user"}'
```

В Swagger:

- открыть `https://ai-bot.vn1.ru/api/docs`
- нажать `Authorize`
- ввести username/password пользователя из Keycloak
- после авторизации вызывать защищенные эндпоинты

Вызов API с токеном:

```bash
curl -X POST 'http://localhost/api/generate/instruction' \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F 'file=@/path/to/instruction.docx'
```

Обновить токен:

```bash
curl -X POST 'http://localhost/api/auth/refresh' \
  -H 'Content-Type: application/json' \
  -d '{"refresh_token": "'"$REFRESH_TOKEN"'"}'
```

## Frontend

Frontend находится в `frontend/` и сделан на Vite + React + TypeScript + Ant Design в стиле проекта
`Dz-otus/frontend`.

Локальный запуск:

```bash
cd frontend
npm install
npm run dev
```

По умолчанию dev-сервер доступен на `http://localhost:5173`, а запросы `/api/*` проксируются на
`http://localhost:8010`.

Production-сборка:

```bash
cd frontend
npm run build
```

В docker-compose frontend собирается отдельным сервисом `frontend`, а внешний nginx проксирует `/` на него.
Страница входа использует backend endpoints `/api/auth/login`, `/api/auth/refresh`, `/api/auth/me`, которые
работают с Keycloak.

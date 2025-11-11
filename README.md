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
sudo docker compose up -d --build n8n-vn1

### обновление завсиимостей

# 1. Обновить образ

sudo docker compose pull
sudo docker compose up -d --force-recreate
docker compose up -d --force-recreate n8n-alliance-trucks

docker image prune -f

# 2. Пересоздать контейнер с новым образом

sudo docker compose down
sudo docker compose up -d

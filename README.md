### Шаги для установки на сервер

## клонируем репо по SSH

ssh-keygen -t ed25519 -C "deor_dima@alliance-trucks"
cat ~/.ssh/id_ed25519.pub
ssh -T git@github.com

## установка гита

sudo apt update
sudo apt install -y git
/opt$ sudo chown -R deor_dima:deor_dima ./
git clone git@github.com:ORG/REPO.git

## установка докер

https://docs.docker.com/engine/install/debian/

sudo apt-get update
sudo apt-get install docker-compose-plugin

sudo docker ps

### обновление завсиимостей

# 1. Обновить образ

sudo docker compose pull
sudo docker compose up -d --force-recreate
docker compose up -d --force-recreate n8n-alliance-trucks

docker image prune -f

# 2. Пересоздать контейнер с новым образом

sudo docker compose down
sudo docker compose up -d

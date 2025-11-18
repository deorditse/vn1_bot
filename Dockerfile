FROM docker.n8n.io/n8nio/n8n:latest

USER root

# Для Alpine нужный пакет pandoc называется "pandoc"
RUN apk update && \
    apk add --no-cache pandoc

USER node
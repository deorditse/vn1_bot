# docker build -t vn1-frontend -f frontend/Dockerfile .
# docker run -d -p 8080:80 vn1-frontend

ARG BASE_HREF=/
ARG APP=/app

FROM node:22-alpine AS build

ARG APP
WORKDIR $APP

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

FROM nginx:1.27-alpine AS deploy

ARG BASE_HREF
ARG APP

RUN rm -rf /usr/share/nginx/html/*
COPY --from=build ${APP}/dist/ /usr/share/nginx/html/${BASE_HREF}
COPY shared/ci-cd/frontend/nginx-default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

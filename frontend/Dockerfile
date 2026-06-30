# docker build -t vn1-frontend -f Dockerfile .
# docker run -d -p 8080:80 vn1-frontend

ARG BASE_HREF=/
ARG APP=/app

FROM node:22-alpine AS build

ARG APP
WORKDIR $APP

COPY ./package*.json ./
RUN npm install

COPY ./ ./
RUN npm run build

FROM nginx:1.27-alpine AS deploy

ARG BASE_HREF
ARG APP

COPY --from=build ${APP}/dist /usr/share/nginx/html/${BASE_HREF}
COPY ci_cd/nginx-default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

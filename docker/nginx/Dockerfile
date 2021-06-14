FROM nginx:1.19.2-alpine
WORKDIR /
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/nginx/nginx.conf /etc/nginx/conf.d
COPY static static

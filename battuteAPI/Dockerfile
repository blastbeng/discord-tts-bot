FROM node:current-alpine3.14

COPY package*.json /tmp/
RUN cd /tmp && npm ci --only=production
RUN mkdir -p /usr/src/app && cp -a /tmp/node_modules /usr/src/app

WORKDIR /usr/src/app

COPY . .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
FROM node:current-alpine3.14

### Create app directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

### Install app dependencies
COPY package.json .
COPY package-lock.json .
RUN npm install

### Copy application source
COPY . .

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
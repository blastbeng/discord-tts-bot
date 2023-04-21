# jerky-tts-bot

A fully functional discord and telegram bot with various functions

## Getting Started

These instructions will give you a copy of the project up and running on
your local or remote machine.

### Prerequisites

Automated install:
- systemd
- docker
- docker-compose

Manual install: 
- docker
- docker-compose

### Installing & Deploy

There are two ways to run this bot, one is by manually using docker-compose 
and another one is by using the convenience script install.sh.

The main difference is that the automated install requires systemd and will 
handle the bot restarts automatically.

- cp .env.sample to .env and edit it with your paarams
- cp one of the docker-compose(one of your choiche) file in the main dir to docker-compose.yml
- run "./install.sh" or docker-compose up
- if using the install.sh script you can use systemd to control the bot (systemctl start/stop/restart docker-compose@jerky-tts-bot)

### Bot Functions

TODO


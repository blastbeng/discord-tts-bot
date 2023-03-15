#!/bin/sh
if [ "$(pwd)" != "/opt/docker/compose" ]; 
then
    mkdir -p /opt/docker/compose/
    cd /opt/docker/compose/
fi

git clone https://github.com/blastbeng/jerky-tts-bot
cd jerky-tts-bot

docker-compose build

mdkdir config
#cp api/uwsgi.ini config/uwsgi.ini

sudo cp ./docker-compose@.service /lib/systemd/system/docker-compose@.service
sudo systemctl daemon-reload
sudo systemctl enable --now docker-compose@jerky-tts-bot.service
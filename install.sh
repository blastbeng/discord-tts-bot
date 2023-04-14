#!/bin/sh
if [ "$(pwd)" != "/opt/docker/compose" ]; 
then
    mkdir -p /opt/docker/compose/
    cd /opt/docker/compose/
fi

git clone https://github.com/blastbeng/jerky-tts-bot
cd jerky-tts-bot

docker compose build

sudo cp ./docker-compose@.service /lib/systemd/system/docker-compose@.service
sudo systemctl daemon-reload
./build-restart.sh
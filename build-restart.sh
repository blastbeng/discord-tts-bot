#!/bin/sh
cd /opt/docker/compose/jerky-tts-bot
docker-compose build
sudo systemctl restart docker-compose@jerky-tts-bot.service
sleep 10
docker-compose logs -f
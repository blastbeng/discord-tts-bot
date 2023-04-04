#!/bin/sh
cd /opt/docker/compose/jerky-tts-bot
#sudo systemctl stop docker-compose@jerky-tts-bot.service
docker compose build
sudo systemctl restart docker-compose@jerky-tts-bot.service
sleep 10
docker compose logs -f

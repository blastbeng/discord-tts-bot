#!/bin/sh
cd /opt/docker/compose/jerky-tts-bot
docker compose build --no-cache
sudo systemctl restart docker-compose@jerky-tts-bot.service

#!/bin/sh
cd /opt/docker/compose/discord-tts-bot
docker compose -f docker-compose.yml build --no-cache
sudo systemctl restart docker-compose@discord-tts-bot.service

#!/bin/sh
cd /opt/docker/compose/jerky-tts-bot
sudo systemctl disable docker-compose@jerky-tts-bot.service --now
docker compose -f docker-compose.yml build jerky-tts-bot-api
docker compose -f docker-compose.yml build jerky-tts-bot-api-balancer
docker compose -f docker-compose.yml build jerky-tts-bot-client
docker compose -f docker-compose.yml build jerky-tts-bot-telegram
docker compose -f docker-compose.yml build jerky-tts-bot-website
sudo systemctl enable docker-compose@jerky-tts-bot.service --now

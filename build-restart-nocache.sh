#!/bin/sh
cd /opt/docker/compose/jerky-tts-bot
sudo rm /opt/docker/compose/jerky-tts-bot/config/download*
sudo rm /opt/docker/compose/jerky-tts-bot/config/markov*
sudo rm /opt/docker/compose/jerky-tts-bot/config/sentences*
docker compose -f docker-compose.yml build jerky-tts-bot-api --no-cache
docker compose -f docker-compose.yml build jerky-tts-bot-client --no-cache
docker compose -f docker-compose.yml build jerky-tts-bot-telegram --no-cache
sudo systemctl restart docker-compose@jerky-tts-bot.service

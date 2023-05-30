#!/bin/sh
cd /opt/docker/compose/discord-tts-bot
sudo rm /opt/docker/compose/discord-tts-bot/config/download*
sudo rm /opt/docker/compose/discord-tts-bot/config/markov*
sudo rm /opt/docker/compose/discord-tts-bot/config/sentences*
docker compose -f docker-compose.yml build discord-tts-bot-api --no-cache
docker compose -f docker-compose.yml build discord-tts-bot-client --no-cache
docker compose -f docker-compose.yml build discord-tts-bot-telegram --no-cache
sudo systemctl restart docker-compose@discord-tts-bot.service

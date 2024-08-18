#!/bin/sh
cd /opt/docker/compose/discord-tts-bot
#sudo rm /opt/docker/compose/discord-tts-bot/config/download*
#sudo rm /opt/docker/compose/discord-tts-bot/config/markov*
#sudo rm /opt/docker/compose/discord-tts-bot/config/sentences*
docker compose -f docker-compose.yml build
sudo systemctl restart docker-compose@discord-tts-bot.service

#!/bin/sh
sudo rm -rf /tmp/discord-voicebot-api/fakeyou_voices.sqlite
sudo systemctl stop docker-compose@discord-voicebot.service
docker-compose build
sudo systemctl start docker-compose@discord-voicebot.service
sleep 10
docker-compose logs -f
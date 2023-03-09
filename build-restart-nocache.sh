#!/bin/sh
cd /opt/docker/compose/discord-voicebot
docker-compose build --no-cache
sudo systemctl restart docker-compose@discord-voicebot.service
sleep 10
docker-compose logs -f
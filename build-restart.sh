#!/bin/sh
docker-compose build
sudo systemctl restart docker-compose@discord-voicebot.service
sleep 10
docker-compose logs -f
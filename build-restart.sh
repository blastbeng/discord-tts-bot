#!/bin/sh
sudo rm -rf /tmp/scemo-pezzente-api/fakeyou_voices.sqlite
sudo systemctl stop docker-compose@scemo-pezzente.service
docker-compose build
sudo systemctl start docker-compose@scemo-pezzente.service
sleep 10
docker-compose logs -f
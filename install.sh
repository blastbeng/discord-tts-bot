#!/bin/sh
if ! [ -x "$(command -v docker)" ]; then
  echo 'Error. Please install docker and docker compose plugin.' >&2
  exit 1
fi
if ! [ -x "$(command -v rclone)" ]; then
  echo 'Error. Please install rclone (Must support crypt).' >&2
  exit 1
fi

if [ "$(pwd)" != "/opt/docker/compose" ]; 
then
    mkdir -p /opt/docker/compose/
    cd /opt/docker/compose/
fi

git clone https://github.com/blastbeng/discord-tts-bot
cd discord-tts-bot


sudo mkdir -p /var/lib/docker-plugins/rclone/config
sudo mkdir -p /var/lib/docker-plugins/rclone/cache

docker plugin install rclone/docker-volume-rclone:amd64 args="-v" --alias rclone --grant-all-permissions

sudo cp rclone/rclone.conf /var/lib/docker-plugins/rclone/config/rclone.conf

PASS=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 32 ; echo '')
RCLONE_PASS=$(echo "$PASS" | rclone obscure -)

sed -i "s/PASSWORD_TEMPLATE/$RCLONE_PASS/" /var/lib/docker-plugins/rclone/config/rclone.conf

cp docker-compose.crypted.full.yml docker-compose.yml

sed -i "s/PASSWORD_TEMPLATE/$RCLONE_PASS/" docker-compose.yml

docker compose build

sudo systemctl enable docker-compose@discord-tts-bot.service
sudo cp ./docker-compose@.service /lib/systemd/system/docker-compose@.service
sudo systemctl daemon-reload
./build-restart.sh

exit 0
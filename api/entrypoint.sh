#!/usr/bin/env bash
mkdir -p /app/config/backups/
cp /app/config/*db.sqlite3 /app/config/backups/
rm -f /tmp/discord-voicebot-api/fakeyou_voices.sqlite
touch /tmp/discord-voicebot-api/uwsgi.sock
chmod 777 -R /tmp/discord-voicebot-api/uwsgi.sock
uwsgi --ini /app/config/uwsgi.ini --enable-threads

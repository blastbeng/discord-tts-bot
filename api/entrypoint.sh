#!/usr/bin/env bash
#mkdir -p /app/config/backups/
#cp /app/config/*db.sqlite3 /app/config/backups/
#rm -f /tmp/jerky-tts-bot-api/fakeyou_voices.sqlite
touch /tmp/jerky-tts-bot-api/uwsgi.sock
chmod 777 -R /tmp/jerky-tts-bot-api/uwsgi.sock
uwsgi --ini /app/uwsgi.ini --enable-threads --log-4xx --log-5xx --disable-logging

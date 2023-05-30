#/bin/bash
/opt/docker/compose/discord-tts-bot/api/.venv/bin/uwsgi --ini /opt/docker/compose/discord-tts-bot/api/uwsgi-local.ini --enable-threads --log-4xx --log-5xx --disable-logging
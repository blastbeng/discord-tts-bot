#!/usr/bin/env bash
rm /app/config/download*
rm /app/config/markov*
rm /app/config/sentences*
uwsgi --ini /app/uwsgi.ini --enable-threads --log-4xx --log-5xx --disable-logging
#uwsgi --ini /app/uwsgi.ini --enable-threads

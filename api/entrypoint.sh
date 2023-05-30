#!/usr/bin/env bash
#uwsgi --ini /app/uwsgi.ini --enable-threads --log-4xx --log-5xx --disable-logging
uwsgi --ini /app/uwsgi.ini --enable-threads

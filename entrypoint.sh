#!/bin/sh

if [ "$DATABASE_URL" = "" ]; then
    echo DATABASE_URL not set, aborting.
    exit 1
fi

python manage.py migrate --check
if [ $? -ne 0 ]; then
    echo running migrations before starting app
    python manage.py migrate
fi

# check the following for logformat
# https://docs.gunicorn.org/en/latest/settings.html#access-log-format

gunicorn -w ${GUNICORN_WORKERS:-1} \
        ocr.wsgi:application \
        --access-logfile - \
        --access-logformat '%(t)s [%(h)s] %(l)s "%(r)s"' \
        --bind 0.0.0.0:8000

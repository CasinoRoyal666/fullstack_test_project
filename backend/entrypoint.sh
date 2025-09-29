#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

if [ "$MODE" = "dev" ]; then
    export DJANGO_SETTINGS_MODULE=config.settings.development
    python manage.py runserver 0.0.0.0:8000
else
    export DJANGO_SETTINGS_MODULE=config.settings.production
    gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
fi

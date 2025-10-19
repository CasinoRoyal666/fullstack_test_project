#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ -n "$1" ]; then
    echo "Executing command: $@"
    exec "$@"
fi

if [ "$MODE" = "dev" ]; then
    echo "Starting development server..."
    export DJANGO_SETTINGS_MODULE=config.settings.development
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting production server (Gunicorn)..."
    export DJANGO_SETTINGS_MODULE=config.settings.production
    exec gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
fi

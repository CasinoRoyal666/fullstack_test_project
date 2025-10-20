#!/bin/bash
set -e

if [ -n "$1" ]; then
    echo "Executing command: $*"
    exec "$@"
fi

if [ "$MODE" = "test" ]; then
    echo "Test mode - skipping migrations and collectstatic"
    exit 0
fi

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

if [ "$MODE" = "dev" ]; then
    echo "Starting development server..."
    export DJANGO_SETTINGS_MODULE=config.settings.development
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting production server (Gunicorn)..."
    export DJANGO_SETTINGS_MODULE=config.settings.production
    exec gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
fi

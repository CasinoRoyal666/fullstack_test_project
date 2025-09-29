FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip==24.3.1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN printf '#!/bin/sh\nset -e\n\npython manage.py migrate --noinput\npython manage.py collectstatic --noinput\n\nif [ "$DJANGO_ENVIRONMENT" = "development" ]; then\n    exec python manage.py runserver 0.0.0.0:8000\nelse\n    exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4\nfi\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

import os
from .base import *

DEBUG = True

# SECRET_KEY = os.getenv(
#     'SECRET_KEY',
#     'django-insecure-dev-key-only-for-development-change-in-prod'
# )

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

#Django Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}
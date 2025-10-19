from .base import *

DEBUG = False

SECRET_KEY = "test"  # nosec B105

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

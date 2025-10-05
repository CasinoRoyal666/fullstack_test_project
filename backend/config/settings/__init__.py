import os
from .base import *

environment = os.getenv('DJANGO_ENVIRONMENT', 'development')
print(f"Loaded environment: '{environment}'")

if environment == 'production':
    from .production import *
    print("Importing prod settings")
else:
    from .development import *
    print("Importing dev settings")
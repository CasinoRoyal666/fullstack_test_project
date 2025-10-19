import os

from .base import *

environment = os.getenv("DJANGO_ENVIRONMENT", "development")
print(f"Loaded environment: '{environment}'")

if environment == "production":
    from .production import *

    print("Importing production settings")

elif environment == "test":
    from .test import *

    print("Importing test settings")

else:
    from .development import *

    print("Importing development settings")

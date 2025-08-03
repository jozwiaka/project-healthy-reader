from django_common.settings.settings_common import *
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS += [
    "books",
    ] 

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("BOOK_DB_NAME"),
        "USER": os.getenv("BOOK_DB_USER"),
        "PASSWORD": os.getenv("BOOK_DB_PASSWORD"),
        "HOST": os.getenv("BOOK_DB_HOST") if RUNNING_IN_DOCKER else "localhost",
        "PORT": os.getenv("BOOK_DB_PORT") if RUNNING_IN_DOCKER else os.getenv("BOOK_DB_LOCAL_PORT"),
    }
}

CACHES["default"]["KEY_PREFIX"] = os.getenv("BOOK_SERVICE", "book_service")

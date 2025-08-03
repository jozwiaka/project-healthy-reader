from django_common.settings.settings_common import *
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS += ["ratings"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("RATING_DB_NAME"),
        "USER": os.getenv("RATING_DB_USER"),
        "PASSWORD": os.getenv("RATING_DB_PASSWORD"),
        "HOST": os.getenv("RATING_DB_HOST") if RUNNING_IN_DOCKER else "localhost",
        "PORT": os.getenv("RATING_DB_PORT") if RUNNING_IN_DOCKER else os.getenv("RATING_DB_LOCAL_PORT"),
    }
}

CACHES["default"]["KEY_PREFIX"] = os.getenv("RATING_SERVICE", "rating_service")

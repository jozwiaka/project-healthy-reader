from django_common.settings.settings_common import *
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS += ["users", "rest_framework_simplejwt"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("USER_DB_NAME"),
        "USER": os.getenv("USER_DB_USER"),
        "PASSWORD": os.getenv("USER_DB_PASSWORD"),
        "HOST": os.getenv("USER_DB_HOST") if RUNNING_IN_DOCKER else "localhost",
        "PORT": os.getenv("USER_DB_PORT") if RUNNING_IN_DOCKER else os.getenv("USER_DB_LOCAL_PORT"),
    }
}

CACHES["default"]["KEY_PREFIX"] = os.getenv("USER_SERVICE", "user_service")

# JWT auth only for user-service
REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"] = (
    "rest_framework_simplejwt.authentication.JWTAuthentication",
)

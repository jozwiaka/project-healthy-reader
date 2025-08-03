FROM python:3.12-slim

WORKDIR /app/services/user-service

COPY ./services/user-service/requirements.txt /app/services/user-service/requirements.txt
COPY ./common/django_common/requirements.txt /app/common/django_common/requirements.txt

RUN pip install --no-cache-dir -r /app/common/django_common/requirements.txt \
    && pip install --no-cache-dir -r /app/services/user-service/requirements.txt

COPY ./services/user-service /app/services/user-service
COPY ./common/django_common /app/common/django_common

ENV RUNNING_IN_DOCKER true

CMD ["sh", "-c", "python manage.py migrate && python manage.py import_users && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers=4 --threads=2 --timeout=60"]

# CMD ["sh", "-c", "python manage.py migrate && python manage.py import_users && python manage.py runserver 0.0.0.0:8000"]


# CMD ["sh", "-c", "python manage.py migrate && python manage.py import_users && python manage.py runserver 0.0.0.0:8000"]

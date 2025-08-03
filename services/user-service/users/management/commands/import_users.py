import csv
import os
import random
import string
from django.core.management.base import BaseCommand
from users.models import User
from django.contrib.auth.hashers import make_password
from config.settings import BASE_DIR

def random_username(existing_usernames, length=8):
    while True:
        username = 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        if username not in existing_usernames:
            return username

def random_email(existing_emails, length=8):
    domains = ['example.com', 'testmail.com', 'mail.com']
    while True:
        email = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + '@' + random.choice(domains)
        if email not in existing_emails:
            return email

def random_password(length=12):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=length))

class Command(BaseCommand):
    help = 'Import users from users.csv with random unique usernames, emails and passwords'

    def handle(self, *args, **kwargs):
        file_path = os.path.join(BASE_DIR, 'data/users.csv')

        self.stdout.write(f'Loading users from {file_path}')

        # Fetch existing usernames and emails to avoid duplicates
        existing_usernames = set(User.objects.values_list('username', flat=True))
        existing_emails = set(User.objects.values_list('email', flat=True))

        with open(file_path, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            users = []
            for row in reader:
                try:
                    age = row['Age']
                    uid = int(row['User-ID'])

                    # Generate unique username and email
                    username = random_username(existing_usernames)
                    existing_usernames.add(username)

                    email = random_email(existing_emails)
                    existing_emails.add(email)

                    raw_password = random_password()
                    
                    hash_password = False

                    users.append(User(
                        id=uid,
                        location=row['Location'],
                        age=int(age) if age.isdigit() else None,
                        username=username,
                        email=email,
                        password=make_password(raw_password) if hash_password else raw_password
                    ))
                except Exception as e:
                    self.stderr.write(f"Skipping row due to error: {e}")

            User.objects.bulk_create(users, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS('Successfully imported users with random credentials'))

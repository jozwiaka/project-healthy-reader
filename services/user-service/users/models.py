from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password as django_check_password

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    password = models.CharField(max_length=128)

    location = models.CharField(max_length=255, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['age']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        return django_check_password(raw_password, self.password)

    def __str__(self):
        return f"User {self.username} ({self.id}) from {self.location or 'Unknown'}"

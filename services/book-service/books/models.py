from django.db import models
from django.utils import timezone

class Author(models.Model):
    name = models.CharField(max_length=255, unique=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "authors"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    year_of_publication = models.PositiveIntegerField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    image_url_s = models.URLField(blank=True, null=True)
    image_url_m = models.URLField(blank=True, null=True)
    image_url_l = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "books"
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} by {self.author.name}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Quote(models.Model):
    text = models.TextField(unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="quotes")
    tags = models.ManyToManyField(Tag, related_name="quotes", blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "quotes"
        ordering = ["author__name"]

    def __str__(self):
        return f"{self.text[:50]}..." if len(self.text) > 50 else self.text

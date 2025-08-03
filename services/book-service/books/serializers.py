from rest_framework import serializers
from .models import Author, Book, Quote, Tag


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "bio", "created_at"]


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = [
            "isbn",
            "title",
            "author",
            "year_of_publication",
            "publisher",
            "image_url_s",
            "image_url_m",
            "image_url_l",
        ]

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class QuoteSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    tags = TagSerializer(many=True)

    class Meta:
        model = Quote
        fields = ["id", "text", "author", "tags", "created_at"]

from rest_framework import viewsets
from rest_framework.response import Response
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
import hashlib
from .models import Book, Quote, Author, Tag
from .serializers import BookSerializer, QuoteSerializer, AuthorSerializer, TagSerializer
import logging

logger = logging.getLogger(__name__)

def make_cache_key(prefix: str, identifier: str = "", query_params: str = "") -> str:
    """Generate consistent cache keys"""
    if query_params:
        query_hash = hashlib.md5(query_params.encode()).hexdigest()
        return f"{prefix}:{identifier}:{query_hash}"
    return f"{prefix}:{identifier}" if identifier else prefix


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("name")
    serializer_class = AuthorSerializer
    lookup_field = "id"

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()
        cache_key = make_cache_key("authors:list", query_params=query_params)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def retrieve(self, request, *args, **kwargs):
        author_id = kwargs.get("id")
        cache_key = make_cache_key("author", identifier=author_id)

        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()  # flush all author caches
        return response

    def update(self, request, *args, **kwargs):
        author_id = kwargs.get("id")
        response = super().update(request, *args, **kwargs)
        cache.delete(make_cache_key("author", identifier=author_id))
        return response

    def destroy(self, request, *args, **kwargs):
        author_id = kwargs.get("id")
        response = super().destroy(request, *args, **kwargs)
        cache.delete(make_cache_key("author", identifier=author_id))
        return response


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author").all()
    serializer_class = BookSerializer
    lookup_field = "isbn"

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["author__name", "publisher", "year_of_publication"]
    ordering_fields = ["title", "year_of_publication"]
    search_fields = ["title", "author__name"]

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()
        cache_key = make_cache_key("books:list", query_params=query_params)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def retrieve(self, request, *args, **kwargs):
        isbn = kwargs.get("isbn")
        cache_key = make_cache_key("book", identifier=isbn)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        isbn = kwargs.get("isbn")
        response = super().update(request, *args, **kwargs)
        cache.delete(make_cache_key("book", identifier=isbn))
        return response

    def destroy(self, request, *args, **kwargs):
        isbn = kwargs.get("isbn")
        response = super().destroy(request, *args, **kwargs)
        cache.delete(make_cache_key("book", identifier=isbn))
        return response


class QuoteViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.select_related("author").prefetch_related("tags").all()
    serializer_class = QuoteSerializer

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()
        cache_key = make_cache_key("quotes:list", query_params=query_params)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def retrieve(self, request, *args, **kwargs):
        quote_id = kwargs.get("pk")
        cache_key = make_cache_key("quote", identifier=quote_id)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        quote_id = kwargs.get("pk")
        response = super().update(request, *args, **kwargs)
        cache.delete(make_cache_key("quote", identifier=quote_id))
        return response

    def destroy(self, request, *args, **kwargs):
        quote_id = kwargs.get("pk")
        response = super().destroy(request, *args, **kwargs)
        cache.delete(make_cache_key("quote", identifier=quote_id))
        return response


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request, *args, **kwargs):
        query_params = request.query_params.urlencode()
        cache_key = make_cache_key("tags:list", query_params=query_params)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def retrieve(self, request, *args, **kwargs):
        tag_id = kwargs.get("pk")
        cache_key = make_cache_key("tag", identifier=tag_id)
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(cached_data)

        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=600)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.clear()
        return response

    def update(self, request, *args, **kwargs):
        tag_id = kwargs.get("pk")
        response = super().update(request, *args, **kwargs)
        cache.delete(make_cache_key("tag", identifier=tag_id))
        return response

    def destroy(self, request, *args, **kwargs):
        tag_id = kwargs.get("pk")
        response = super().destroy(request, *args, **kwargs)
        cache.delete(make_cache_key("tag", identifier=tag_id))
        return response

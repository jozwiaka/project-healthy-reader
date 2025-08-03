from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer
import logging
from django_common.utils.cache import make_cache_key  # <- your utils.py

logger = logging.getLogger(__name__)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        cache_key = make_cache_key("user", identifier=str(user_id))
        #logger.info("Retrieve called for user_id=%s", user_id)

        # Try cache
        user_data = cache.get(cache_key)
        if user_data:
            #logger.info("CACHE HIT for key: %s", cache_key)
            return Response(user_data)

        # Cache miss, fetch from DB
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        #logger.info("CACHE SET for key: %s", cache_key)
        return response

    def list(self, request, *args, **kwargs):
        # Use query params in the cache key (so different filters don’t collide)
        query_string = request.META.get("QUERY_STRING", "")
        cache_key = make_cache_key("users", identifier="list", query_params=query_string)
        #logger.info("List called with cache_key=%s", cache_key)

        # Try cache
        user_data = cache.get(cache_key)
        if user_data:
            #logger.info("CACHE HIT for key: %s", cache_key)
            return Response(user_data)

        # Cache miss
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = list(serializer.data)

        cache.set(cache_key, data, timeout=300)
        #logger.info("CACHE SET for key: %s", cache_key)
        return Response(data)

    def create(self, request, *args, **kwargs):
        #logger.info("Create called")
        response = super().create(request, *args, **kwargs)
        # Invalidate all user list caches
        cache.delete_pattern("users:list*")
        #logger.info("CACHE DELETED for keys matching: users:list*")
        return response

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        response = super().update(request, *args, **kwargs)
        # Invalidate caches
        cache.delete(make_cache_key("user", identifier=str(user_id)))
        cache.delete_pattern("users:list*")
        #logger.info("CACHE DELETED for user:%s and users:list*", user_id)
        return response

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        #logger.info("Destroy called for user_id=%s", user_id)
        response = super().destroy(request, *args, **kwargs)
        # Invalidate caches
        cache.delete(make_cache_key("user", identifier=str(user_id)))
        cache.delete_pattern("users:list*")
        #logger.info("CACHE DELETED for user:%s and users:list*", user_id)
        return response

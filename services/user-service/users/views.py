from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

# Cache key helpers
def user_cache_key(user_id):
    return f"user:{user_id}"

def user_list_cache_key():
    return "users:list"

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        cache_key = user_cache_key(user_id)
        logger.info("Retrieve called for user_id=%s", user_id)

        # Try cache
        user_data = cache.get(cache_key)
        if user_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(user_data)

        # Cache miss, fetch from DB
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return response

    def list(self, request, *args, **kwargs):
        cache_key = user_list_cache_key()
        logger.info("List called")

        # Try cache
        user_data = cache.get(cache_key)
        if user_data:
            logger.info("CACHE HIT for key: %s", cache_key)
            return Response(user_data)

        # Cache miss
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = list(serializer.data)  # <-- convert to plain list

        cache.set(cache_key, data, timeout=300)
        logger.info("CACHE SET for key: %s", cache_key)
        return Response(data)


    def create(self, request, *args, **kwargs):
        logger.info("Create called")
        response = super().create(request, *args, **kwargs)
        # Invalidate list cache
        cache.delete(user_list_cache_key())
        logger.info("CACHE DELETED for key: %s", user_list_cache_key())
        return response

    def update(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        response = super().update(request, *args, **kwargs)
        # Invalidate caches
        cache.delete(user_cache_key(user_id))
        cache.delete(user_list_cache_key())
        logger.info("CACHE DELETED for keys: %s, %s", user_cache_key(user_id), user_list_cache_key())
        return response

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        logger.info("Destroy called for user_id=%s", user_id)
        response = super().destroy(request, *args, **kwargs)
        # Invalidate caches
        cache.delete(user_cache_key(user_id))
        cache.delete(user_list_cache_key())
        logger.info("CACHE DELETED for keys: %s, %s", user_cache_key(user_id), user_list_cache_key())
        return response

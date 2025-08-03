# docker exec -it project-healthy-reader-user-service-1 python manage.py shell -c "from django.conf import settings; print(settings.CACHES)"
# docker exec -it project-healthy-reader-user-service-1 python -c "import redis; r=redis.Redis(host='redis', port=6379, password='dev-redis-pass'); print(r.ping())"
# docker exec -it project-healthy-reader-user-service-1 sh -c "apt update && apt install -y redis-tools && redis-cli -h redis -a dev-redis-pass ping"
# python manage.py shell -c "from django.core.cache import cache; cache.set('test_key','hello',60); print('Cache set'); print('Cache get:', cache.get('test_key')); cache.delete('test_key'); print('Cache deleted'); print('Cache after delete:', cache.get('test_key'))"

docker exec -it project-healthy-reader-user-service-1 python manage.py shell -c "from django.core.cache import cache; cache.set('ping','pong',60); print(cache.get('ping'))"
docker exec -it project-healthy-reader-redis-1 redis-cli -a dev-redis-pass KEYS "*"

curl http://localhost:8080/api/v1/users/1
curl http://localhost:8080/api/v1/users/1
docker exec -it project-healthy-reader-redis-1 redis-cli -a dev-redis-pass KEYS "*"
curl http://localhost:8080/api/v1/users/
curl http://localhost:8080/api/v1/users/
docker exec -it project-healthy-reader-redis-1 redis-cli -a dev-redis-pass KEYS "*"

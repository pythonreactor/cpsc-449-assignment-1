import redis
import os

redis_client = redis.StrictRedis(
    host=os.getenv('REDIS_HOST', 'fim-redis'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

"""
This module is a wrapper for flask_caching. It configures it and rename
the memoize function. The aim with that cache is to minimize the requests
made on the target database.
"""

import redis

from flask_caching import Cache
from zou.app import config


cache = None

try:
    redis_cache = redis.StrictRedis(
        host=config.KEY_VALUE_STORE["host"],
        port=config.KEY_VALUE_STORE["port"],
        db=config.MEMOIZE_DB_INDEX,
        password=config.KEY_VALUE_STORE["password"],
        decode_responses=True,
    )
    redis_cache.get("test")
    cache = Cache(
        config={
            "CACHE_TYPE": "redis",
            "CACHE_REDIS_HOST": config.KEY_VALUE_STORE["host"],
            "CACHE_REDIS_PORT": config.KEY_VALUE_STORE["port"],
            "CACHE_REDIS_DB": config.MEMOIZE_DB_INDEX,
            "CACHE_REDIS_PASSWORD": config.KEY_VALUE_STORE["password"],
        }
    )

# This is needed to run tests which. This way they do not require a Redis
# instance to work properly
except redis.ConnectionError:
    cache = Cache(config={"CACHE_TYPE": "simple"})

memoize_function = cache.memoize


def invalidate(*args):
    cache.delete_memoized(*args)


def clear():
    cache.clear()

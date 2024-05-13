from flask import (
    current_app,
    g
)
from flask_pymongo import PyMongo
from iam import settings
from redis import Redis
from werkzeug.local import LocalProxy

logger = settings.getLogger(__name__)


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = PyMongo(current_app).db

    return db


def get_redis_conn():
    """
    Configuration method to return Redis instance
    """
    redis_conn = getattr(g, '_redis_conn', None)

    if redis_conn is None:
        redis_conn = g._redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    return redis_conn


db    = LocalProxy(get_db)
cache = LocalProxy(get_redis_conn)

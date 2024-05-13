from elasticsearch import Elasticsearch
from flask import (
    current_app,
    g
)
from flask_pymongo import PyMongo
from inventory import settings
from redis import Redis
from rq import Queue
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


def get_redis_queue():
    """
    Configuration method to return rq Queue instance
    """
    redis_queue = getattr(g, '_redis_queue', None)

    if redis_queue is None:
        redis_conn  = get_redis_conn()
        redis_queue = g._redis_queue = Queue(connection=redis_conn, name='inventory-service')

    return redis_queue


def get_elasticsearch():
    """
    Configuration method to return an elasticsearch instance
    """
    es = getattr(g, '_es', None)

    if es is None:
        es = g._es = Elasticsearch(hosts=[current_app.config['ELASTICSEARCH_URL']])

    return es


db          = LocalProxy(get_db)
cache       = LocalProxy(get_redis_conn)
redis_queue = LocalProxy(get_redis_queue)
es          = LocalProxy(get_elasticsearch)

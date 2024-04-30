"""
This script is used to initialize an iPython shell with the Flask app context.
"""
import logging

from elasticsearch import Elasticsearch
from flask import (
    Flask,
    g
)
from flask_pymongo import PyMongo
from inventory import settings
from redis import Redis
from rq import Queue
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MONGO_URI'] = settings.FlaskConfig.MONGO_URI


def setup_database_indexes(database: PyMongo):
    """
    Prepare the database indexes if they don't exist.
    """
    for collection_name, indexes in settings.MONGO_INDEXES.items():
        collection = getattr(database, collection_name)

        # Handle this one at a time to allow for proper error logging
        for index in indexes:
            try:
                collection.create_indexes([index])
            except Exception:
                logger.error('Failed to generate %s index %s', collection_name, index.document.get('name'))
                pass


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = PyMongo(app).db

    logger.info('Generating database indexes...')
    setup_database_indexes(database=db)

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
            db=settings.REDIS_DB
        )

    return redis_conn


def get_redis_queue():
    """
    Configuration method to return rq Queue instance
    """
    redis_queue = getattr(g, '_redis_queue', None)

    if redis_queue is None:
        redis_conn  = get_redis_conn()
        redis_queue = g._redis_queue = Queue(connection=redis_conn, name='ipython')

    return redis_queue


def get_elasticsearch():
    """
    Configuration method to return an elasticsearch instance
    """
    es = getattr(g, '_es', None)

    if es is None:
        es = g._es = Elasticsearch(hosts=[settings.ELASTICSEARCH_URL])

    return es


db          = LocalProxy(get_db)
redis_conn  = LocalProxy(get_redis_conn)
redis_queue = LocalProxy(get_redis_queue)
es          = LocalProxy(get_elasticsearch)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'app': app,
        'redis_conn': redis_conn,
        'redis_queue': redis_queue,
        'es': es
    }


ctx = app.app_context()
ctx.push()

print('Initialized iPython shell with Flask app context.')

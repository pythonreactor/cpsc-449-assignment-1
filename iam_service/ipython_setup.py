"""
This script is used to initialize an iPython shell with the Flask app context.
"""
import logging

from flask import (
    Flask,
    g
)
from flask_pymongo import PyMongo
from iam import settings
from redis import Redis
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
    db = getattr(g, "_database", None)

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


db         = LocalProxy(get_db)
redis_conn = LocalProxy(get_redis_conn)


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'redis_conn': redis_conn,
        'app': app
    }


ctx = app.app_context()
ctx.push()

print('Initialized iPython shell with Flask app context.')

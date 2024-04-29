import logging

from flask import (
    current_app,
    g
)
from flask_pymongo import PyMongo
from iam import settings
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)


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
        db = g._database = PyMongo(current_app).db

    logger.info('Generating database indexes...')
    setup_database_indexes(database=db)

    return db


db = LocalProxy(get_db)

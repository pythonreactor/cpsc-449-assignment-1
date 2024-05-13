from __future__ import annotations

from typing import TYPE_CHECKING

from iam import (
    db,
    models,
    settings
)

logger = settings.getLogger(__name__)


if TYPE_CHECKING:
    from flask_pymongo import PyMongo


def setup_database_indexes(database: PyMongo = db):
    """
    Prepare the database indexes if they don't exist.
    """
    logger.info('Generating database indexes...')

    for collection_name, indexes in settings.MONGO_INDEXES.items():
        collection = getattr(database, collection_name)

        # Handle this one at a time to allow for proper error logging
        for index in indexes:
            try:
                collection.create_indexes([index])
            except Exception:
                logger.error('Failed to generate %s index %s', collection_name, index.document.get('name'))
                pass


def login_user(user: models.User) -> models.IAMAuthToken:
    """
    Fetch a user's auth token or create a new one
    """
    logger.info('[%s] Generating new user auth token', user.email)
    del user.token

    token      = models.IAMAuthToken()
    user.token = token

    try:
        user.save()
    except Exception:
        logger.exception('Error creating new auth token for user: %s', user.email)
        raise

    return token

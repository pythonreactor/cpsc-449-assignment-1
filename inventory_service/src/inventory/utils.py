from __future__ import annotations

from typing import TYPE_CHECKING

from inventory import (
    db,
    es,
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


def prepare_es_indexes():
    logger.info('Generating Elasticsearch indexes...')

    indexes = settings.ELASTICSEARCH_INDEXES
    for index_name, index_settings in indexes.items():
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=index_settings)
            logger.info('Created index %s in Elasticsearch.', index_name)
        else:
            logger.info('Index %s already exists in Elasticsearch.', index_name)

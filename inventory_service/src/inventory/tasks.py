from __future__ import annotations

import json
import logging
from typing import (
    TYPE_CHECKING,
    Dict
)

from inventory import (
    es,
    redis_conn
)
from rq.decorators import job

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from fim.schemas import FIMObjectID
    from inventory.models import Inventory


@job('default', connection=redis_conn, timeout=500)
def add_item_to_index(index_name: str, item: Inventory, user: dict) -> Dict:
    """
    Add an item to the Elasticsearch index.
    """
    try:
        logger.info('Adding %s to the %s index', item.id, index_name)

        item_data            = item.model_dump()
        item_data['user_id'] = str(user['id'])

        response = es.index(index=index_name, id=item.id, body=item_data)
        return json.dumps(response.body)

    except Exception as e:
        logger.exception('Failed to add item to index: %s', e)


@job('default', connection=redis_conn, timeout=500)
def update_item_in_index(index_name: str, item: Inventory, user: dict) -> Dict:
    """
    Update an item in the Elasticsearch index.
    """
    try:
        logger.info('Updating %s in the %s index', item.id, index_name)

        item_data            = item.model_dump()
        item_data['user_id'] = str(user['id'])

        response = es.update(index=index_name, id=item.id, body={'doc': item_data})
        return json.dumps(response.body)

    except Exception as e:
        logger.exception('Failed to update item in index: %s', e)


@job('default', connection=redis_conn, timeout=500)
def delete_item_in_index(index_name: str, item_id: FIMObjectID) -> Dict:
    """
    Delete an item in the Elasticsearch index.
    """
    try:
        logger.info('Deleting %s in the %s index', item_id, index_name)

        response = es.delete(index=index_name, id=item_id)
        return json.dumps(response.body)

    except Exception as e:
        logger.exception('Failed to delete item in index: %s', e)

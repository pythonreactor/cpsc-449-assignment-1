from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict
)

from flask_pymongo.wrappers import Collection
from inventory import redis_queue as queue
from inventory import (
    schemas,
    settings
)
from inventory.tasks import (
    add_item_to_index,
    delete_item_in_index,
    update_item_in_index
)

logger = settings.getLogger(__name__)


if TYPE_CHECKING:
    from flask_pymongo import PyMongo


class Inventory(schemas.InventoryModel):
    """
    Inventory model
    """

    @classmethod
    @property
    def db(cls) -> PyMongo:
        from inventory import db

        return db

    @classmethod
    @property
    def collection(cls) -> Collection:
        return getattr(cls.db, settings.MONGO_COLLECTION_NAME)

    @property
    def user(self) -> Dict:
        from flask import g

        return getattr(g, 'user', None)

    @user.setter
    def user(self, user: Dict) -> None:
        if not user:
            raise ValueError('user cannot be None')
        elif not isinstance(user, Dict):
            raise TypeError('user must be an instance of User')

        logger.info('Setting user for inventory item')
        self.user_id = user['id']

    @user.deleter
    def user(self) -> None:
        raise NotImplementedError('Cannot delete a user from an inventory item')

    def add_to_index(self, index: str) -> None:
        """
        Add the document to the search index.
        """
        job = queue.enqueue(add_item_to_index, index_name=index, item=self, user=self.user)
        logger.info('Queued job %s to add an item to the %s index', job.id, index)
        return

    def update_index(self, index: str) -> None:
        """
        Update a document in the search index.
        """
        job = queue.enqueue(update_item_in_index, index_name=index, item=self, user=self.user)
        logger.info('Queued job %s to update an item in the %s index', job.id, index)
        return

    def remove_from_index(self, index: str) -> None:
        """
        Remove a document from the search index.
        """
        job = queue.enqueue(delete_item_in_index, index_name=index, item_id=self.id)
        logger.info('Queued job %s to delete an item in the %s index', job.id, index)
        return

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name} ({self.pk})>'

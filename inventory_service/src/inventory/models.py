from __future__ import annotations

import logging
from typing import (
    TYPE_CHECKING,
    Dict
)

from flask_pymongo.wrappers import Collection
from inventory import (
    schemas,
    settings
)

logger = logging.getLogger(__name__)


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

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name} ({self.pk})>'

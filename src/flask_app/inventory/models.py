import logging

from flask_pymongo.wrappers import Collection
from iam.models import User
from inventory import schemas

from flask_app import db

logger = logging.getLogger(__name__)


class Inventory(schemas.InventoryModel):
    """
    Inventory model
    """

    @classmethod
    @property
    def collection(cls) -> Collection:
        return db.inventory

    @property
    def user(self) -> User:
        return User.query.get(_id=self.user_id)

    @user.setter
    def user(self, user: User) -> None:
        if not user:
            raise ValueError('user cannot be None')
        elif not isinstance(user, User):
            raise TypeError('user must be an instance of User')

        logger.info('Setting user for inventory item')
        self.user_id = user.id

    @user.deleter
    def user(self) -> None:
        raise NotImplementedError('Cannot delete a user from an inventory item')

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name} ({self.pk})>'

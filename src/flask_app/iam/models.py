import datetime
import logging
from typing import Optional

import bcrypt
from base import schemas as base_schemas
from flask_pymongo.wrappers import Collection
from iam import schemas
from iam.interface import UserQueryInterface

from flask_app import db

logger = logging.getLogger(__name__)


class IAMAuthToken(schemas.AuthTokenModel):
    """
    IAM Authentication Token model
    """

    @classmethod
    @property
    def query(cls) -> None:
        raise NotImplementedError('Cannot directly query the IAMAuthToken model.')

    @property
    def is_valid(self) -> bool:
        logger.info('Validating user auth token')

        if self.expired:
            return False

        self.refresh()
        return True

    def refresh(self) -> None:
        """
        Refresh the token's updated_at value to prevent it from becoming
        stale.
        """
        self.updated_at = datetime.datetime.utcnow()

    def delete(self) -> None:
        raise AttributeError('Cannot directly delete an IAMAuthToken instance.')

    def __repr__(self):
        return f'<{self.__class__.__name__}: {"Expired" if self.expired else "Valid"}>'


class User(schemas.UserModel):
    """
    User model
    """

    # inventory = db.relationship('Inventory', backref='user', lazy=True, cascade='all, delete-orphan')

    @classmethod
    @property
    def collection(cls) -> Collection:
        return db.users

    @classmethod
    @property
    def query(cls) -> UserQueryInterface:
        """
        Class property to access the Model Query interface.
        """
        if not hasattr(cls, '_query_interface'):
            cls._query_interface = UserQueryInterface(cls)

        return cls._query_interface

    @property
    def full_name(self) -> str:
        return f'{self.first_name.title()} {self.last_name.title()}'

    @property
    def token(self) -> Optional[IAMAuthToken]:
        if token := self.auth_token:
            if token.expired:
                logger.warning('User auth token has expired.')

                del self.token
                return

            return IAMAuthToken(**token.dict())

    @token.setter
    def token(self, value: Optional[IAMAuthToken]) -> None:
        self.auth_token = value

    @token.deleter
    def token(self) -> None:
        if self.auth_token:
            self.auth_token = None
            self.save()

    def refresh_token(self) -> None:
        """
        Refresh an AuthToken's updated_at value to prevent it from becoming
        stale/expired
        """
        logger.info('Refreshing user auth token.')

        if not self.token or not self.token.is_valid():
            return

        self.token.refresh()
        self.save()

    def delete_token(self) -> None:
        logger.info('Removing user auth token.')

        del self.token
        self.save()

    def verify_password(self, password: str) -> str:
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.email}>'

    class Config(schemas.UserModel.Config):
        arbitrary_types_allowed = True
        json_encoders = {base_schemas.FIMObjectID: lambda v: str(v)}

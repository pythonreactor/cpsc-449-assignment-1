from typing import (
    TYPE_CHECKING,
    Optional
)

from fim.interface import QueryInterface

if TYPE_CHECKING:
    from models import User


class UserQueryInterface(QueryInterface):

    def find_by_email(self, email: str) -> Optional['User']:
        document = self.model.collection.find_one({'email': email})
        if not document:
            return None

        return self.model(**document)

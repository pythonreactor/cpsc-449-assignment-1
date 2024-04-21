from typing import Optional

from base.interface import QueryInterface


class UserQueryInterface(QueryInterface):

    def find_by_email(self, email: str) -> Optional['User']:
        document = self.model.collection.find_one({'email': email})
        if not document:
            return None

        return self.model(**document)

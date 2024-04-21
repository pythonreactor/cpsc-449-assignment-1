from __future__ import annotations

from dataclasses import dataclass
from typing import (
    Generic,
    List,
    Optional,
    TypeVar
)

from pydantic import (
    BaseModel,
    Field
)

T = TypeVar('T', bound=BaseModel)


@dataclass
class QuerySet(Generic[T]):
    """
    Custom dataclass to represent a queryset (emmulating an ORM like Django).
    """
    items: List[T] = Field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index: int):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        if len(self.items) > 5:
            return f'<QuerySet: {self.items[:5]}...>'
        else:
            return f'<QuerySet: {self.items}>'

    def __str__(self):
        return '<QuerySet>'

    def count(self) -> int:
        return self.__len__()

    def first(self) -> Optional[T]:
        return self.items[0] if self.items else None

    def last(self) -> Optional[T]:
        return self.items[-1] if self.items else None

    def filter(self, **kwargs) -> 'QuerySet[T]':
        return [item for item in self.items if all(getattr(item, field) == value for field, value in kwargs.items())]

    def order_by(self, field: str, direction: str = 'asc') -> 'QuerySet[T]':
        self.items.sort(key=lambda item: getattr(item, field), reverse=direction.lower() == 'desc')
        return self

    def paginate(self, page: int, per_page: int) -> PaginatedQuerySet[T]:
        start = (page - 1) * per_page
        end   = start + per_page

        return PaginatedQuerySet(
            items=self.items[start:end],
            total=len(self.items),
            pages=max(len(self.items) // per_page, 1),
            next_page=page + 1 if end < len(self.items) else None,
            prev_page=page - 1 if start > 0 else None
        )

    def delete(self) -> None:
        for item in self.items:
            item.delete()


@dataclass
class PaginatedQuerySet(QuerySet):
    """
    Custom dataclass to represent a paginated QuerySet.
    """
    total: int = 0
    pages: int = 0
    next_page: Optional[int] = None
    prev_page: Optional[int] = None

    def __repr__(self):
        if len(self.items) > 5:
            return f'<PaginatedQuerySet: {self.items[:5]}...>'
        else:
            return f'<PaginatedQuerySet: {self.items}>'

    def __str__(self):
        return '<PaginatedQuerySet>'


class QueryInterface:

    def __init__(self, model):
        self.model = model

    def __repr__(self):
        return f'<QueryInterface for {self.model.__name__}>'

    def get(self, **kwargs):
        """
        Find a single document based on keyword arguments.
        """
        query = {field: value for field, value in kwargs.items()}
        if 'id' in query:
            query['pk'] = query.pop('id')

        document = self.model.collection.find_one(query)
        data     = self.model(**document) if document else None

        return data

    def find_by_id(self, id: 'FIMObjectID') -> Optional['BaseFlaskModel']:
        """
        Find a document by its ObjectId and return it as an instance of its
        corresponding model.
        """
        document = self.model.collection.find_one({'_id': id})
        if not document:
            return None

        return self.model(**document)

    def filter(self, **kwargs) -> QuerySet['BaseFlaskModel']:
        """
        Perform a filter operation based on keyword arguments.
        """
        query = {}
        for field, value in kwargs.items():
            if isinstance(value, list):
                query[field] = {'$in': value}
            else:
                query[field] = value

        if 'id' in query:
            query['pk'] = query.pop('id')

        documents = self.model.collection.find(query)
        data      = [self.model(**document) for document in documents]

        return QuerySet(data)

    def all(self) -> QuerySet['BaseFlaskModel']:
        """
        Find all documents in a collection and return them as instances of their
        corresponding models.
        """
        documents = self.model.collection.find()
        data      = [self.model(**document) for document in documents]

        return QuerySet(data)

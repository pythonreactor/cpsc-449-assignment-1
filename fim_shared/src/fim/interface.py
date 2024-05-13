from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Generic,
    Optional,
    TypeVar
)

from fim.settings import getLogger
from pydantic import (
    BaseModel,
    Field
)

logger = getLogger(__name__)


if TYPE_CHECKING:
    from collections.abc import Iterable

    from fim.models import BaseFlaskModel
    from fim.schemas import FIMObjectID


T = TypeVar('T', bound=BaseModel)


# region MongoDB Interface

@dataclass
class QuerySet(Generic[T]):
    """
    Custom dataclass to represent a MongoDB queryset (emmulating an ORM like Django).
    """
    items: list[T] = Field(default_factory=list)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> T:
        return self.items[index]

    def __iter__(self) -> Iterable[T]:
        return iter(self.items)

    def __repr__(self) -> str:
        if len(self.items) > 5:
            return f'<QuerySet: {self.items[:5]}...>'
        else:
            return f'<QuerySet: {self.items}>'

    def __str__(self) -> str:
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
    Custom dataclass to represent a paginated MongoDB QuerySet.
    """
    total: int = 0
    pages: int = 0
    next_page: Optional[int] = None
    prev_page: Optional[int] = None

    def __repr__(self) -> str:
        if len(self.items) > 5:
            return f'<PaginatedQuerySet: {self.items[:5]}...>'
        else:
            return f'<PaginatedQuerySet: {self.items}>'

    def __str__(self) -> str:
        return '<PaginatedQuerySet>'


class QueryInterface:

    def __init__(self, model):
        self.model = model

    def __repr__(self) -> str:
        return f'<QueryInterface for {self.model.__name__}>'

    def get(self, **kwargs) -> Optional[BaseFlaskModel]:
        """
        Find a single document based on keyword arguments.
        """
        query = {field: value for field, value in kwargs.items()}
        if 'id' in query:
            query['pk'] = query.pop('id')

        document = self.model.collection.find_one(query)
        data     = self.model(**document) if document else None

        return data

    def find_by_id(self, id: FIMObjectID) -> Optional[BaseFlaskModel]:
        """
        Find a document by its ObjectId and return it as an instance of its
        corresponding model.
        """
        document = self.model.collection.find_one({'_id': id})
        if not document:
            return None

        return self.model(**document)

    def filter(self, **kwargs) -> QuerySet[BaseFlaskModel]:
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

    def all(self) -> QuerySet[BaseFlaskModel]:
        """
        Find all documents in a collection and return them as instances of their
        corresponding models.
        """
        documents = self.model.collection.find()
        data      = [self.model(**document) for document in documents]

        return QuerySet(data)

# endregion


# region Elasticsearch Interface

@dataclass
class ElasticsearchQuerySet(Generic[T]):
    """
    Custom dataclass to represent a queryset for Elasticsearch (emulating an ORM like Django).
    """
    items: list[T] = Field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index: int):
        return self.items[index]

    def __iter__(self) -> Iterable[T]:
        return iter(self.items)

    def count(self) -> int:
        return self.__len__()

    def first(self) -> Optional[T]:
        return self.items[0] if self.items else None

    def last(self) -> Optional[T]:
        return self.items[-1] if self.items else None

    def filter(self, **kwargs) -> 'ElasticsearchQuerySet[T]':
        return [item for item in self.items if all(getattr(item, field) == value for field, value in kwargs.items())]

    def paginate(self, page: int, per_page: int) -> PaginatedElasticsearchQuerySet[T]:
        start = (page - 1) * per_page
        end   = start + per_page

        return PaginatedElasticsearchQuerySet(
            items=self.items[start:end],
            total=len(self.items),
            pages=max(len(self.items) // per_page, 1),
            next_page=page + 1 if end < len(self.items) else None,
            prev_page=page - 1 if start > 0 else None
        )

    def delete(self) -> None:
        # TODO: Delete from ES index
        pass


@dataclass
class PaginatedElasticsearchQuerySet(ElasticsearchQuerySet):
    """
    Custom dataclass to represent a paginated Elasticsearch QuerySet.
    """
    total: int = 0
    pages: int = 0
    next_page: Optional[int] = None
    prev_page: Optional[int] = None

    def __repr__(self) -> str:
        if len(self.items) > 5:
            return f'<PaginatedElasticsearchQuerySet: {self.items[:5]}...>'
        else:
            return f'<PaginatedElasticsearchQuerySet: {self.items}>'

    def __str__(self) -> str:
        return '<PaginatedElasticsearchQuerySet>'


class ElasticsearchQueryInterface:

    def __init__(self, model):
        # NOTE: These imports are in here to prevent potential circular
        # import issues.
        from elasticsearch import (
            Elasticsearch,
            NotFoundError
        )
        from flask import (
            current_app,
            g
        )

        try:
            self.index_name = model.index
        except Exception:
            raise AttributeError(f'{model.__name__} must have an `index` attribute')

        self.model = model
        self.es    = getattr(
            g,
            '_es',
            Elasticsearch(hosts=[current_app.config['ELASTICSEARCH_URL']])
        )
        self.not_found_error = NotFoundError

    def __repr__(self) -> str:
        return f'<ElasticsearchQueryInterface for {self.model.__name__}>'

    def get(self, **kwargs) -> Optional[BaseFlaskModel]:
        """
        Find a single document based on keyword arguments.
        """
        query = {field: value for field, value in kwargs.items()}
        if 'id' in query:
            query['pk'] = query.pop('id')

        response = self.es.search(index=self.model.index, body={'query': {'match': query}})
        hits     = response['hits']['hits']

        if hits:
            return self.model(**hits[0]['_source'])
        else:
            logger.info('Document not found in %s index', self.model.index)
            return None

    def find_by_id(self, id: FIMObjectID) -> Optional[BaseFlaskModel]:
        """
        Find a document by its ObjectId and return it as an instance of its
        corresponding model.
        """
        try:
            response = self.es.get(index=self.model.index, id=id)
            return self.model(**response['_source']) if response['found'] else None
        except self.NotFoundError:
            logger.info('Document not found in %s index', self.model.index)
            return None

    def filter(self, **kwargs) -> ElasticsearchQuerySet[BaseFlaskModel]:
        """
        Perform a filter operation based on keyword arguments.
        """
        query = {k: v for k, v in kwargs.items()}
        if 'id' in query:
            query['pk'] = query.pop('id')

        if query:
            es_query = {'query': {'bool': {'must': [{'match': query}]}}}
        else:
            return self.all()
        response = self.es.search(index=self.model.index, body=es_query)
        hits     = response['hits']['hits']
        data     = [self.model(**hit['_source']) for hit in hits]

        return ElasticsearchQuerySet(data)

    def search(self, query: dict) -> ElasticsearchQuerySet[BaseFlaskModel]:
        """
        Perform a search operation based on keyword arguments.
        """
        user_id = query.pop('user_id', None)

        if not query:
            raise ValueError('Query must contain at least one search term')

        if user_id:
            es_query = {
                'query': {
                    'bool': {
                        'must': [
                            {'term': {'user_id': user_id}},
                            {
                                'bool': {
                                    'should': [{'wildcard': {k: f'*{v}*'}} for k, v in query.items()],
                                    'minimum_should_match': 1
                                }
                            }
                        ]
                    }
                }
            }
        else:
            es_query = {
                'query': {
                    'query_string': {
                        'query': f'*{v}*',
                        'fields': [k],
                        'default_operator': 'OR'
                    }
                }
                for k, v in query.items()
            }

        response = self.es.search(index=self.model.index, body=es_query)
        data     = [self.model(**hit['_source']) for hit in response['hits']['hits']]

        return ElasticsearchQuerySet(data)

    def all(self) -> ElasticsearchQuerySet[BaseFlaskModel]:
        """
        Find all items in an index and return them as instances of their
        corresponding models.
        """
        response = self.es.search(index=self.model.index)
        data     = [self.model(**hit['_source']) for hit in response['hits']['hits']]

        return ElasticsearchQuerySet(data)

# endregion

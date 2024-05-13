from __future__ import annotations

import datetime
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Optional,
    Type
)

from fim import (
    schemas,
    settings
)
from fim.interface import (
    ElasticsearchQueryInterface,
    QueryInterface,
    T
)
from flask_pymongo.wrappers import Collection
from pymongo import errors

logger = settings.getLogger(__name__)


if TYPE_CHECKING:
    from flask_pymongo import PyMongo


class BaseFlaskModel(schemas.BaseModelSchema):

    @property
    @abstractmethod
    def db(cls) -> PyMongo:
        """
        Define the database for the model.
        """
        raise NotImplementedError('Calling from the base class')

    @property
    @abstractmethod
    def collection(cls) -> Collection:
        """
        Define the collection for the model.
        """
        raise NotImplementedError('Calling from the base class')

    @classmethod
    @property
    def index(cls) -> str:
        """
        Class property to return the model's Elasticsearch index name.
        """
        module = cls.__module__.split('.')[0]
        uses_es = getattr(__import__(f'{module}.settings', fromlist=['*']), 'ELASTICSEARCH_INDEXES', None)

        if not uses_es:
            raise NotImplementedError('This service does not utilize Elasticsearch')

        return cls.__name__.lower()

    @classmethod
    @property
    def query(cls: Type[T]) -> QueryInterface:
        """
        Class property to access the Model Query interface.
        """
        if not hasattr(cls, '_query_interface'):
            cls._query_interface = QueryInterface(cls)

        return cls._query_interface

    @classmethod
    @property
    def es_query(cls: Type[T]) -> ElasticsearchQueryInterface:
        """
        Class property to access the Model Elasticsearch Query interface.
        """
        if not hasattr(cls, '_es_query_interface'):
            cls._es_query_interface = ElasticsearchQueryInterface(cls)

        return cls._es_query_interface

    @classmethod
    def __next_pk(cls) -> int:
        """
        Increment and retun the next pk number for a given collection.
        """
        pk_document = cls.db.counters.find_one_and_update(
            {'_id': cls.collection.name},
            {'$inc': {'seq': 1}},
            upsert=True,
            return_document=True,
            new=True
        )
        return pk_document['seq']

    @classmethod
    def __rollback_pk(cls) -> None:
        """
        Decrement the current pk number for a given collection.
        """
        cls.db.counters.find_one_and_update(
            {'_id': cls.collection.name},
            {'$inc': {'seq': -1}},
            upsert=False
        )

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new document in the collection and return it as an instance of
        its corresponding model.
        """
        obj    = cls(**kwargs)
        obj.pk = cls.__next_pk()

        try:
            result = cls.collection.insert_one(obj.model_dump(override=False))
        except errors.DuplicateKeyError as e:
            logger.error('Duplicate key error: %s', e.details['keyValue'])

            cls.__rollback_pk()
            raise errors.DuplicateKeyError(e.details['keyValue'])

        if not result.acknowledged:
            raise Exception(f'Failed to create {cls.__name__} document')

        new_obj = cls.query.find_by_id(result.inserted_id)
        if not new_obj:
            raise Exception(f'Failed to find newly created {cls.__name__} document')

        return new_obj

    def delete(self) -> None:
        """
        Delete a document from the collection.
        """
        logger.info('[%s:%s] Deleting document', self.__class__.__name__, self.id)
        self.collection.delete_one({'_id': self.id})

    def refresh_from_db(self) -> Optional['BaseFlaskModel']:
        """
        Refresh the current instance with the latest data from the database.
        """
        document = self.collection.find_one({'_id': self.id})
        if not document:
            return None

        self = self.__class__(**document)

    def add_to_index(self, index: str) -> None:
        """
        Add the document to the search index.
        """
        raise NotImplementedError('Method not implemented')

    def update_index(self, index: str) -> None:
        """
        Update a document in the search index.
        """
        raise NotImplementedError('Method not implemented')

    def remove_from_index(self, index: str) -> None:
        """
        Remove a document from the search index.
        """
        raise NotImplementedError('Method not implemented')

    def save(self):
        """
        Save the current instance to the database.
        """
        self.updated_at = datetime.datetime.utcnow()

        document = self.model_dump(override=False)
        self.collection.update_one(
            {'_id': self.id},
            {'$set': document}
        )


class BasePKFlaskModel(schemas.BasePKModelSchema, BaseFlaskModel):
    """
    Base model for Flask models with a primary key.
    """
    ...

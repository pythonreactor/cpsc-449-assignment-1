import logging
from http import HTTPStatus
from typing import (
    Dict,
    List,
    Optional
)

import pydantic
from flask import jsonify
from flask.views import MethodView
from flask_sqlalchemy import (
    SQLAlchemy,
    model
)
from flask_sqlalchemy.query import Query

from flask_app.base.authentication import BaseAuthentication
from flask_app.base.constants import SortDirectionEnum
from flask_app.base.schemas import (
    BaseDeleteQuerySchema,
    BaseDeleteResponseSchema,
    BaseDetailQuerySchema,
    BaseDetailResponseSchema,
    BaseListQuerySchema,
    BaseListResponseSchema,
    InternalServerErrorResponseSchema,
    NotFoundResponseSchema
)
from flask_app.iam.authentication import protected_view

logger = logging.getLogger(__name__)


# TODO: Add permissions


class BaseListAPI(MethodView):
    """
    Base list API meant to be used for viewing a list of objects
    """
    authentication_class = BaseAuthentication

    request_query_schema: pydantic.BaseModel = BaseListQuerySchema
    request_body_schema: pydantic.BaseModel = None
    response_schema: pydantic.BaseModel = BaseListResponseSchema

    db: SQLAlchemy = None
    model: model = None
    default_ordering_field: str = ''
    default_ordering_dir: str = SortDirectionEnum.Ascending.value

    def _get_ordering_from_request(self, query: request_query_schema) -> [str, str]:
        """
        Prepare the ordering for the queryset
        """
        ordering_field = query.order_by or self.__class__.default_ordering_field
        direction = query.direction or self.__class__.default_ordering_dir

        return direction, ordering_field

    def _get_pagination_from_request(self, query: request_query_schema) -> Dict:
        return {'page': query.page, 'per_page': query.per_page}

    def _get_filters_from_request(self, query: request_query_schema) -> List:
        """
        Get filters from the request to be used on the queryset
        """
        filters = list()

        if query.id_in and type(query.id_in) == list:
            field = getattr(self.__class__.model, 'id')
            filters.append(field.in_(query.id_in))

        return filters

    def _get_queryset(self, query: request_query_schema) -> Query:
        """
        Get a queryset for the given model
        """
        # TODO: Add permissions here
        subject_model = self.__class__.model
        initial_queryset = subject_model.query

        direction, ordering_field = self._get_ordering_from_request(query=query)
        if ordering_field:
            order_by = getattr(self.__class__.model, ordering_field)

            if direction == SortDirectionEnum.Ascending.value:
                order_by = order_by.asc()
            elif direction == SortDirectionEnum.Descending.value:
                order_by = order_by.desc()

        pagination = self._get_pagination_from_request(query=query)

        filters = self._get_filters_from_request(query=query)
        if filters:
            initial_queryset = initial_queryset.filter(*filters)

        queryset: query.Query.paginate = initial_queryset.order_by(order_by).paginate(**pagination, error_out=False)

        return queryset

    @protected_view
    def get(self, query: request_query_schema):
        try:
            queryset = self._get_queryset(query=query)
        except Exception:
            err_msg = f'Error building a {self.__class__.model.__name__} queryset'
            logger.exception(err_msg)

            return jsonify(InternalServerErrorResponseSchema(message=err_msg).dict()), HTTPStatus.INTERNAL_SERVER_ERROR

        response_data = [obj.obj_schema for obj in queryset.items]
        pagination_data = {
            'total': queryset.total,
            'pages': queryset.pages,
            'next_page': queryset.next_num,
            'prev_page': queryset.prev_num
        }

        return jsonify(self.__class__.response_schema(data=response_data, pagination=pagination_data).dict(exclude_none=True)), HTTPStatus.OK


class BaseDetailAPI(MethodView):
    """
    Base detail API meant to be used for viewing and updating a single object
    """
    authentication_class = BaseAuthentication

    request_query_schema: pydantic.BaseModel = BaseDetailQuerySchema
    request_body_schema: pydantic.BaseModel = None
    response_schema: pydantic.BaseModel = BaseDetailResponseSchema

    db: SQLAlchemy = None
    model: model = None

    def _get_instance(self, pk: int) -> model:
        subject_model = self.__class__.model
        return subject_model.query.filter_by(id=pk).first()

    @protected_view
    def get(self, query: request_query_schema):
        obj = self._get_instance(pk=query.id)
        if not obj:
            err_msg = f'{self.__class__.model.__name__} with id {query.id} not found'
            return jsonify(NotFoundResponseSchema(message=err_msg).dict()), HTTPStatus.NOT_FOUND

        return jsonify(self.__class__.response_schema(data=obj.obj_schema).dict()), HTTPStatus.OK

    @protected_view
    def patch(self, query: request_query_schema, body: request_body_schema):
        obj = self._get_instance(pk=query.id)
        if not obj:
            err_msg = f'{self.__class__.model.__name__} with id {query.id} not found'
            return jsonify(NotFoundResponseSchema(message=err_msg).dict()), HTTPStatus.NOT_FOUND

        for field, value in body.model_dump().items():
            setattr(obj, field, value)

        try:
            self.__class__.db.session.commit()
        except Exception:
            err_msg = f'Error updating {self.__class__.model.__name__} object with id {query.id}'
            logger.exception(err_msg)

            self.__class__.db.session.rollback()
            return jsonify(InternalServerErrorResponseSchema(message=err_msg).dict()), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify(self.__class__.response_schema(data=obj.obj_schema).dict()), HTTPStatus.OK


class BaseDeleteAPI(MethodView):
    """
    Base delete API meant to be used for deleting one or many objects.
    """
    authentication_class = BaseAuthentication

    request_query_schema: pydantic.BaseModel = BaseDeleteQuerySchema
    response_schema: pydantic.BaseModel = BaseDeleteResponseSchema

    db: SQLAlchemy = None
    model: model = None

    def _get_filters_from_request(self, query: request_query_schema) -> List:
        """
        Get filters from the request to be used on the queryset
        """
        filters = list()

        if query.id_in and type(query.id_in) == list:
            field = getattr(self.__class__.model, 'id')
            filters.append(field.in_(query.id_in))

        return filters

    def _get_queryset(self, query: request_query_schema) -> Query:
        """
        Get a queryset for the given model
        """
        # TODO: Add permissions here
        subject_model = self.__class__.model
        initial_queryset = subject_model.query

        filters = self._get_filters_from_request(query=query)
        if filters:
            queryset = initial_queryset.filter(*filters)
        else:
            queryset: List = initial_queryset.filter_by(id=query.id)

        return queryset

    @protected_view
    def delete(self, query: request_query_schema):
        queryset: Query = self._get_queryset(query=query)
        if not queryset.count():
            err_msg = f'No {self.__class__.model.__name__} objects found'
            return jsonify(NotFoundResponseSchema(message=err_msg).dict()), HTTPStatus.NOT_FOUND

        try:
            queryset.delete()
            self.__class__.db.session.commit()
            self.__class__.db.session.expire_all()
        except Exception:
            err_msg = f'Error deleting {self.__class__.model.__name__} objects'
            logger.exception(err_msg)

            self.__class__.db.session.rollback()
            return jsonify(InternalServerErrorResponseSchema(message=err_msg).dict()), HTTPStatus.INTERNAL_SERVER_ERROR

        return jsonify(self.__class__.response_schema().dict()), HTTPStatus.RESET_CONTENT

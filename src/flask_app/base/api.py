import logging
from http import HTTPStatus
from typing import (
    Dict,
    List
)

import pydantic
from flask import (
    g,
    jsonify
)
from flask.views import MethodView
from flask_sqlalchemy import (
    SQLAlchemy,
    model
)
from flask_sqlalchemy.query import Query

from flask_app.base.authentication import BaseAuthentication
from flask_app.base.constants import SortDirectionEnum
from flask_app.base.schemas import (
    BaseBulkCreateResponseSchema,
    BaseBulkDeleteRequestSchema,
    BaseBulkDeleteResponseSchema,
    BaseCreateResponseSchema,
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


class BaseCreateAPI(MethodView):
    """
    Base Create API meant to be used for creating a single object
    """
    authentication_class = BaseAuthentication

    request_body_schema: pydantic.BaseModel = None
    response_schema: pydantic.BaseModel = BaseCreateResponseSchema

    db: SQLAlchemy = None
    model: model = None

    def _generate_new_obj(self, body: request_body_schema, user: model = None, relate_user: bool = True) -> model:
        """
        Generate a new object for the given model
        """
        subject_model = self.__class__.model

        new_obj_data = body.model_dump()

        if relate_user:
            new_obj_data['user_id'] = user.id

        new_obj = subject_model(**new_obj_data)

        return new_obj

    @protected_view
    def post(self, body: request_body_schema):
        user = getattr(g, 'user', self.__class__.authentication_class.user)

        # TODO: Add permissions here
        new_obj = self._generate_new_obj(body=body, user=user)

        self.__class__.db.session.add(new_obj)
        try:
            self.__class__.db.session.commit()
            response_message = f'new {self.__class__.model.__name__} object created successfully'

            return jsonify(self.__class__.response_schema(message=response_message, data=new_obj.obj_schema).dict()), HTTPStatus.CREATED

        except Exception:
            err_msg = f'Error creating new {self.__class__.model.__name__} object'
            logger.exception(err_msg)

            self.__class__.db.session.rollback()
            return jsonify(InternalServerErrorResponseSchema(message=err_msg).dict()), HTTPStatus.INTERNAL_SERVER_ERROR


class BaseBulkCreateAPI(BaseCreateAPI):
    """
    Base Bulk Create API meant to be used for creating many objects
    """
    authentication_class = BaseAuthentication

    request_body_schema: pydantic.BaseModel = None
    response_schema: pydantic.BaseModel = BaseBulkCreateResponseSchema

    db: SQLAlchemy = None
    model: model = None

    @protected_view
    def post(self, body: request_body_schema):
        user = getattr(g, 'user', self.__class__.authentication_class.user)
        new_objs = list()

        # TODO: Add permissions here
        for item in body.items:
            new_obj = self._generate_new_obj(body=item, user=user)
            new_objs.append(new_obj)

        self.__class__.db.session.add_all(new_objs)
        try:
            self.__class__.db.session.commit()
            response_message = f'new {self.__class__.model.__name__} objects created successfully'
            response_data = [obj.obj_schema for obj in new_objs]

            return jsonify(self.__class__.response_schema(message=response_message, data=response_data).dict()), HTTPStatus.CREATED

        except Exception:
            err_msg = f'Error creating new {self.__class__.model.__name__} objects'
            logger.exception(err_msg)

            self.__class__.db.session.rollback()
            return jsonify(InternalServerErrorResponseSchema(message=err_msg).dict()), HTTPStatus.INTERNAL_SERVER_ERROR


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
        user = getattr(g, 'user', self.__class__.authentication_class.user)
        subject_model = self.__class__.model

        if hasattr(subject_model, 'user_id'):
            initial_queryset = subject_model.query.filter(subject_model.user_id == user.id)
        else:
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
        user = getattr(g, 'user', self.__class__.authentication_class.user)
        subject_model = self.__class__.model
        instance = subject_model.query.filter_by(id=pk).first()

        if hasattr(subject_model, 'user_id') and instance and not instance.user_id == user.id:
            return None

        return instance

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

        for field, value in body.model_dump(exclude_none=True).items():
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
    Base delete API meant to be used for deleting a single object
    """
    authentication_class = BaseAuthentication

    request_query_schema: pydantic.BaseModel = BaseDeleteQuerySchema
    response_schema: pydantic.BaseModel = BaseDeleteResponseSchema

    db: SQLAlchemy = None
    model: model = None

    def _get_queryset(self, query: request_query_schema) -> Query:
        """
        Get a queryset for the given model
        """
        user = getattr(g, 'user', self.__class__.authentication_class.user)
        subject_model = self.__class__.model
        queryset = subject_model.query.filter(subject_model.user_id == user.id).filter(subject_model.id == query.id)

        return queryset

    @protected_view
    def delete(self, query: request_query_schema):
        queryset: Query = self._get_queryset(query=query)

        if not queryset.count():
            err_msg = f'No {self.__class__.model.__name__} with id {query.id} found'
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


class BaseBulkDeleteAPI(MethodView):
    """
    Base delete API meant to be used for deleting one or many objects
    """
    authentication_class = BaseAuthentication

    request_body_schema: pydantic.BaseModel = BaseBulkDeleteRequestSchema
    response_schema: pydantic.BaseModel = BaseDeleteResponseSchema

    db: SQLAlchemy = None
    model: model = None

    def _get_queryset(self, body: request_body_schema) -> Query:
        """
        Get a queryset for the given model
        """
        user = getattr(g, 'user', self.__class__.authentication_class.user)
        subject_model = self.__class__.model
        queryset = subject_model.query.filter(subject_model.user_id == user.id).filter(subject_model.id.in_(body.ids))

        return queryset

    @protected_view
    def delete(self, body: request_body_schema):
        queryset: Query = self._get_queryset(body=body)
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

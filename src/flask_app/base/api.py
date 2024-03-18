import logging
from http import HTTPStatus

from flask import jsonify
from flask.views import MethodView
from flask_sqlalchemy.query import Query

from flask_app.base.constants import SortDirectionEnum
from flask_app.base.schemas import (
    BaseDetailQuerySchema,
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
    authentication_class = None

    request_query_schema: 'pydantic.BaseModel' = BaseDetailQuerySchema
    request_body_schema: 'pydantic.BaseModel' = None
    response_schema: 'pydantic.BaseModel' = None

    db: 'SQLAlchemy' = None
    model: 'SQLAlchemy.Model' = None
    default_ordering_field: str = ''
    default_ordering_dir: str = SortDirectionEnum.Ascending.value

    def _get_queryset(self) -> Query:
        """
        Get a queryset for the given model
        """
        subject_model = self.__class__.model

        # TODO: Add permissions here

        return subject_model.query

    def _get_ordering_from_request(self, query: request_query_schema) -> [str, str]:
        """
        Prepare the ordering for the queryset
        """
        ordering_field = query.order_by or self.__class__.default_ordering_field
        direction = query.direction or self.__class__.default_ordering_dir

        return direction, ordering_field

    def _get_pagination_from_request(self, query: request_query_schema) -> dict:
        return {'page': query.page, 'per_page': query.per_page}

    @protected_view
    def get(self, query: request_query_schema):
        order_by = None

        queryset = self._get_queryset()
        direction, ordering_field = self._get_ordering_from_request(query=query)

        if ordering_field:
            order_by = getattr(self.__class__.model, ordering_field)

            if direction == SortDirectionEnum.Ascending.value:
                order_by = order_by.asc()
            elif direction == SortDirectionEnum.Descending.value:
                order_by = order_by.desc()

        pagination = self._get_pagination_from_request(query=query)

        try:
            queryset: query.Query.paginate = queryset.order_by(order_by).paginate(**pagination, error_out=False)
        except Exception:
            err_msg = f'Error ordering {self.__class__.model.__name__} queryset by {ordering_field}'
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
    authentication_class = None

    request_query_schema: 'pydantic.BaseModel' = BaseDetailQuerySchema
    request_body_schema: 'pydantic.BaseModel' = None
    response_schema: 'pydantic.BaseModel' = None

    db: 'SQLAlchemy' = None
    model: 'SQLAlchemy.Model' = None

    def _get_instance(self, pk: int) -> 'SQLAlchemy.Model':
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

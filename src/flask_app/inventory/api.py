import logging
from http import HTTPStatus

from flask_openapi3 import APIView

import flask_app.inventory.models as inventory_models
from flask_app import settings
from flask_app.base.api import (
    BaseBulkCreateAPI,
    BaseBulkDeleteAPI,
    BaseCreateAPI,
    BaseDeleteAPI,
    BaseDetailAPI,
    BaseListAPI
)
from flask_app.base.schemas import (
    BadRequestResponseSchema,
    UnauthorizedResponseSchema
)
from flask_app.common.tags import inventory_tag
from flask_app.iam.authentication import (
    IAMTokenAuthentication,
    protected_view
)
from flask_app.inventory import db
from flask_app.inventory.schemas import (
    InventoryBulkCreateRequestSchema,
    InventoryBulkCreateResponseSchema,
    InventoryBulkDeleteRequestSchema,
    InventoryBulkDeleteResponseSchema,
    InventoryCreateRequestSchema,
    InventoryCreateResponseSchema,
    InventoryDeleteQuerySchema,
    InventoryDeleteResponseSchema,
    InventoryDetailQuerySchema,
    InventoryDetailRequestSchema,
    InventoryDetailResponseSchema,
    InventoryListQuerySchema,
    InventoryListResponseSchema
)

logger = logging.getLogger(__name__)
api_view_v1 = APIView(url_prefix='/api/v1')


@api_view_v1.route('/inventory/create')
class InventoryCreateAPI(BaseCreateAPI):
    """
    API endpoint for creating an inventory item
    """
    authentication_class = IAMTokenAuthentication

    request_body_schema = InventoryCreateRequestSchema
    response_schema = InventoryCreateResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Create API POST',
        summary='Create inventory item',
        description='This endpoint is used to create a new inventory item.',
        responses={
            HTTPStatus.CREATED: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def post(self, body: request_body_schema):
        return super().post(body)


@api_view_v1.route('/inventory/create/bulk')
class InventoryBulkCreateAPI(BaseBulkCreateAPI):
    """
    API endpoint for creating multiple inventory items
    """
    authentication_class = IAMTokenAuthentication

    request_body_schema = InventoryBulkCreateRequestSchema
    response_schema = InventoryBulkCreateResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Bulk Create API POST',
        summary='Create many inventory items',
        description='This endpoint is used to create many inventory items.',
        responses={
            HTTPStatus.CREATED: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def post(self, body: request_body_schema):
        return super().post(body)


@api_view_v1.route('/inventory')
class InventoryListAPI(BaseListAPI):
    """
    API endpoint for listing inventory items
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = InventoryListQuerySchema
    response_schema = InventoryListResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory List API GET',
        summary='List inventory items',
        description='This endpoint is used to list inventory items in the system.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def get(self, query: request_query_schema):
        return super().get(query)


@api_view_v1.route('/inventory')
class InventoryDetailAPI(BaseDetailAPI):
    """
    API endpoint for viewing or updating a single inventory item
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = InventoryDetailQuerySchema
    request_body_schema = InventoryDetailRequestSchema
    response_schema = InventoryDetailResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Detail API GET',
        summary='Inventory detail endpoint',
        description='This endpoint is used to view a single inventory item.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def get(self, query: request_query_schema):
        return super().get(query)

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Detail API PATCH',
        summary='Inventory detail endpoint',
        description='This endpoint is used to update a single inventory item.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def patch(self, query: request_query_schema, body: request_body_schema):
        return super().patch(query, body)


@api_view_v1.route('/inventory/delete')
class InventoryDeleteAPI(BaseDeleteAPI):
    """
    API endpoint for deleting a single inventory object
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = InventoryDeleteQuerySchema
    response_schema = InventoryDeleteResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Delete API DELETE',
        summary='Inventory delete endpoint',
        description='This endpoint is used to delete a single inventory item.',
        responses={
            HTTPStatus.RESET_CONTENT: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def delete(self, query: request_query_schema):
        return super().delete(query)


@api_view_v1.route('/inventory/delete/bulk')
class InventoryBulkDeleteAPI(BaseBulkDeleteAPI):
    """
    API endpoint for deleting many inventory objects
    """
    authentication_class = IAMTokenAuthentication

    request_body_schema = InventoryBulkDeleteRequestSchema
    response_schema = InventoryBulkDeleteResponseSchema

    db = db
    model = inventory_models.Inventory

    @api_view_v1.doc(
        tags=[inventory_tag],
        operation_id='Inventory Bulk Delete API DELETE',
        summary='Inventory bulk delete endpoint',
        description='This endpoint is used to delete many inventory items.',
        responses={
            HTTPStatus.RESET_CONTENT: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def delete(self, body: request_body_schema):
        return super().delete(body)

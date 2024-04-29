import logging
from http import HTTPStatus

from fim.api import (
    BaseBulkCreateAPI,
    BaseBulkDeleteAPI,
    BaseCreateAPI,
    BaseDetailAPI,
    BaseListAPI
)
from fim.authentication import protected_view
from fim.schemas import (
    BadRequestResponseSchema,
    UnauthorizedResponseSchema
)
from flask_openapi3 import APIView
from inventory import (
    models,
    settings
)
from inventory.authentication import TokenAuthentication
from inventory.schemas import (
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
from inventory.tags import inventory_tag

logger = logging.getLogger(__name__)
api_view_v1 = APIView(url_prefix='/api/v1')


@api_view_v1.route('/inventory/create')
class InventoryCreateAPI(BaseCreateAPI):
    """
    API endpoint for creating an inventory item
    """
    authentication_class = TokenAuthentication

    request_body_schema = InventoryCreateRequestSchema
    response_schema     = InventoryCreateResponseSchema

    model = models.Inventory

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
    authentication_class = TokenAuthentication

    request_body_schema = InventoryBulkCreateRequestSchema
    response_schema     = InventoryBulkCreateResponseSchema

    model = models.Inventory

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


@api_view_v1.route('/inventory/items')
class InventoryListAPI(BaseListAPI):
    """
    API endpoint for listing inventory items
    """
    authentication_class = TokenAuthentication

    request_query_schema = InventoryListQuerySchema
    response_schema      = InventoryListResponseSchema

    model = models.Inventory

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


@api_view_v1.route('/inventory/items/<id>')
class InventoryDetailAPI(BaseDetailAPI):
    """
    API endpoint for viewing or updating a single inventory item
    """
    authentication_class = TokenAuthentication

    request_query_schema = InventoryDetailQuerySchema
    request_body_schema  = InventoryDetailRequestSchema
    response_schema      = InventoryDetailResponseSchema

    delete_request_query_schema = InventoryDeleteQuerySchema
    delete_response_schema      = InventoryDeleteResponseSchema

    model = models.Inventory

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


@api_view_v1.route('/inventory/items/delete/bulk')
class InventoryBulkDeleteAPI(BaseBulkDeleteAPI):
    """
    API endpoint for deleting many inventory objects
    """
    authentication_class = TokenAuthentication

    request_body_schema = InventoryBulkDeleteRequestSchema
    response_schema     = InventoryBulkDeleteResponseSchema

    model = models.Inventory

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

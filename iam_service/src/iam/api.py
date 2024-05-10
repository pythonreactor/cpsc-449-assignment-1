import logging
from http import HTTPStatus

from fim.api import (
    BaseBulkDeleteAPI,
    BaseDetailAPI,
    BaseListAPI
)
from fim.authentication import (
    protected_view,
    superuser_view
)
from fim.schemas import (
    BadRequestResponseSchema,
    NotFoundResponseSchema,
    UnauthorizedResponseSchema
)
from flask import (
    jsonify,
    session
)
from flask_openapi3 import APIView
from iam import (
    models,
    settings
)
from iam.authentication import IAMTokenAuthentication
from iam.schemas import (
    ExternalAuthenticationResponseSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    SignupRequestSchema,
    SignupResponseSchema,
    UserBulkDeleteRequestSchema,
    UserBulkDeleteResponseSchema,
    UserDeleteQuerySchema,
    UserDeleteResponseSchema,
    UserDetailQuerySchema,
    UserDetailRequestSchema,
    UserDetailResponseSchema,
    UserListQuerySchema,
    UserListResponseSchema
)
from iam.tags import (
    external_tag,
    iam_tag,
    superuser_tag
)
from iam.utils import login_user
from iam.redis_client import redis_client  # Added Redis import

logger = logging.getLogger(__name__)
internal_api_v1 = APIView(url_prefix='/api/v1')
external_api_v1 = APIView(url_prefix='/api/v1/iam')


# region Internal service APIs

@internal_api_v1.route('/signup')
class SignupAPI:

    @internal_api_v1.doc(
        tags=[iam_tag],
        operation_id='Signup API POST',
        summary='New user signup',
        description='This endpoint is used to create a new user account.',
        responses={
            HTTPStatus.CREATED: SignupResponseSchema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema
        },
        security=None
    )
    def post(self, body: SignupRequestSchema):
        new_user_data = body.model_dump(exclude=['confirm_password'])
        new_user_data['username'] = new_user_data['email']

        try:
            models.User.create(**new_user_data)
            return jsonify(SignupResponseSchema(message='new user created successfully').dict()), HTTPStatus.CREATED
        except Exception:
            logger.exception('Error creating new user: %s', new_user_data['email'])
            return jsonify(BadRequestResponseSchema(message='error creating new user').dict()), HTTPStatus.BAD_REQUEST


@internal_api_v1.route('/login')
class LoginAPI:
    """
    API endpoint for logging into the system
    """

    @internal_api_v1.doc(
        tags=[iam_tag],
        operation_id='Login API POST',
        summary='User login',
        description='This endpoint is used to log into the system and receive an auth token.',
        responses={
            HTTPStatus.OK: LoginResponseSchema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.NOT_FOUND: NotFoundResponseSchema
        },
        security=None
    )
    def post(self, body: LoginRequestSchema):
        cache_key = f"user:{body.email}"
        cached_user = redis_client.get(cache_key)

        if cached_user:
            user = models.User(**eval(cached_user))
        else:
            user = models.User.query.find_by_email(email=body.email)

        if not user:
            return jsonify(NotFoundResponseSchema(message='user not found').dict()), HTTPStatus.NOT_FOUND

        if not user.verify_password(body.password):
            return jsonify(BadRequestResponseSchema(message='invalid password').dict()), HTTPStatus.BAD_REQUEST

        redis_client.setex(cache_key, 300, str(user.model_dump()))  # Cache for 5 minutes

        token = login_user(user)
        session['user_id'] = str(user.id)

        return jsonify(LoginResponseSchema(message='auth token generated', email=user.email, token=token.key).dict()), HTTPStatus.OK


@internal_api_v1.route('/users')
class UserListAPI(BaseListAPI):
    """
    API endpoint for listing all users
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = UserListQuerySchema
    response_schema = UserListResponseSchema

    model = models.User

    @internal_api_v1.doc(
        tags=[iam_tag],
        operation_id='User List API GET',
        summary='List all users',
        description='This endpoint is used to list all users in the system.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def get(self, query: request_query_schema):
        cache_key = "all_users"
        cached_users = redis_client.get(cache_key)

        if cached_users:
            return jsonify(eval(cached_users)), HTTPStatus.OK

        response = super().get(query)

        if response.status_code == HTTPStatus.OK:
            redis_client.setex(cache_key, 300, str(response.get_json()))  # Cache for 5 minutes

        return response


@internal_api_v1.route('/users/<id>')
class UserDetailAPI(BaseDetailAPI):
    """
    API endpoint for viewing, updating, or deleting a single user
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = UserDetailQuerySchema
    request_body_schema = UserDetailRequestSchema
    response_schema = UserDetailResponseSchema

    delete_request_query_schema = UserDeleteQuerySchema
    delete_response_schema = UserDeleteResponseSchema

    model = models.User

    @internal_api_v1.doc(
        tags=[iam_tag],
        operation_id='User Detail API GET',
        summary='User detail endpoint',
        description='This endpoint is used to view a single user.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def get(self, query: request_query_schema):
        cache_key = f"user:{query.id}"
        cached_user = redis_client.get(cache_key)

        if cached_user:
            return jsonify(eval(cached_user)), HTTPStatus.OK

        response = super().get(query)

        if response.status_code == HTTPStatus.OK:
            redis_client.setex(cache_key, 300, str(response.get_json()))  # Cache for 5 minutes

        return response

    @internal_api_v1.doc(
        tags=[iam_tag],
        operation_id='User Detail API PATCH',
        summary='User detail update endpoint',
        description='This endpoint is used to update a user account details.',
        responses={
            HTTPStatus.OK: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema,
            HTTPStatus.NOT_FOUND: NotFoundResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @protected_view
    def patch(self, query: request_query_schema, body: request_body_schema):
        cache_key = f"user:{query.id}"
        response = super().patch(query, body)

        if response.status_code == HTTPStatus.OK:
            redis_client.setex(cache_key, 300, str(response.get_json()))  # Cache for 5 minutes

        return response

    @internal_api_v1.doc(
        tags=[superuser_tag],
        operation_id='Superuser User API DELETE',
        summary='Superuser only: User delete endpoint',
        description='Superuser only: This endpoint is used to delete a single user.',
        responses={
            HTTPStatus.RESET_CONTENT: delete_response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @superuser_view
    def delete(self, query: delete_request_query_schema):
        cache_key = f"user:{query.id}"
        response = super().delete(query)

        if response.status_code == HTTPStatus.RESET_CONTENT:
            redis_client.delete(cache_key)

        return response


@internal_api_v1.route('/users/delete/bulk')
class UserBulkDeleteAPI(BaseBulkDeleteAPI):
    """
    Superuser API endpoint for deleting a batch of users
    """
    authentication_class = IAMTokenAuthentication

    request_body_schema = UserBulkDeleteRequestSchema
    response_schema = UserBulkDeleteResponseSchema

    model = models.User

    @internal_api_v1.doc(
        tags=[superuser_tag],
        operation_id='Superuser User Bulk Delete API DELETE',
        summary='Superuser only: User bulk delete endpoint',
        description='Superuser only: This endpoint is used to delete many users.',
        responses={
            HTTPStatus.RESET_CONTENT: response_schema,
            HTTPStatus.BAD_REQUEST: BadRequestResponseSchema,
            HTTPStatus.UNAUTHORIZED: UnauthorizedResponseSchema
        },
        security=settings.API_TOKEN_SECURITY
    )
    @superuser_view
    def delete(self, body: request_body_schema):
        response = super().delete(body)

        if response.status_code == HTTPStatus.RESET_CONTENT:
            redis_client.delete("all_users")  # Invalidate cache for user list

        return response

# endregion


# region External service APIs

@external_api_v1.route('/authenticate')
class ExternalAuthenticationAPI:

    authentication_class = IAMTokenAuthentication

    response_schema = ExternalAuthenticationResponseSchema

    def post(self):
        auth_response = self.authentication_class()
        if not auth_response.authenticated:
            return auth_response.response

        user_obj = auth_response.user
        user_data = user_obj.model_dump()
        # NOTE: Force the MongoDB ObjectID into the response so the calling service
        # can use it for document referencing
        user_data['id'] = str(user_obj.id)

        token_obj = auth_response.token
        token_data = token_obj.model_dump()

        response_body = self.response_schema(user=user_data, token=token_data)
        return jsonify(response_body.dict()), HTTPStatus.OK

# endregion

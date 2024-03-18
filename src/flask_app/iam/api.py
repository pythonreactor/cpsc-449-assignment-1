import logging
from http import HTTPStatus

from flask import (
    jsonify,
    session
)
from flask_openapi3 import APIView

import flask_app.iam.models as iam_models
from flask_app import settings
from flask_app.base.api import (
    BaseDetailAPI,
    BaseListAPI
)
from flask_app.base.schemas import (
    BadRequestResponseSchema,
    NotFoundResponseSchema,
    UnauthorizedResponseSchema
)
from flask_app.common.tags import iam_tag
from flask_app.iam import db
from flask_app.iam.authentication import (
    IAMTokenAuthentication,
    protected_view
)
from flask_app.iam.schemas import (
    LoginRequestSchema,
    LoginResponseSchema,
    SignupRequestSchema,
    SignupResponseSchema,
    UserDetailQuerySchema,
    UserDetailRequestSchema,
    UserDetailResponseSchema,
    UserListQuerySchema,
    UserListResponseSchema
)
from flask_app.iam.utils import login_user

logger = logging.getLogger(__name__)
api_view_v1 = APIView(url_prefix='/api/v1', view_tags=[iam_tag])


@api_view_v1.route('/signup')
class SignupAPI:

    @api_view_v1.doc(
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

        new_user = iam_models.User(**new_user_data)
        db.session.add(new_user)

        try:
            db.session.commit()
            return jsonify(SignupResponseSchema(message='new user created successfully').dict()), HTTPStatus.CREATED
        except Exception:
            logger.exception('Error creating new user: %s', new_user_data['email'])

            db.session.rollback()
            return jsonify(BadRequestResponseSchema(message='error creating new user').dict()), HTTPStatus.BAD_REQUEST


@api_view_v1.route('/login')
class LoginAPI:
    """
    API endpoint for logging into the system
    """

    @api_view_v1.doc(
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
        user = iam_models.User.query.filter_by(email=body.email).first()
        if not user:
            return jsonify(NotFoundResponseSchema(message='user not found').dict()), HTTPStatus.NOT_FOUND

        if not user.verify_password(body.password):
            return jsonify(BadRequestResponseSchema(message='invalid password').dict()), HTTPStatus.BAD_REQUEST

        token = login_user(user)
        session['user_id'] = user.id

        return jsonify(LoginResponseSchema(message='auth token generated', email=user.email, token=token.key).dict()), HTTPStatus.OK


@api_view_v1.route('/users')
class UserListAPI(BaseListAPI):
    """
    API endpoint for listing all users
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = UserListQuerySchema
    response_schema = UserListResponseSchema

    db = db
    model = iam_models.User

    @api_view_v1.doc(
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
        return super().get(query)


@api_view_v1.route('/user/<int:id>')
class UserDetailAPI(BaseDetailAPI):
    """
    API endpoint for viewing or updating a single user
    """
    authentication_class = IAMTokenAuthentication

    request_query_schema = UserDetailQuerySchema
    request_body_schema = UserDetailRequestSchema
    response_schema = UserDetailResponseSchema

    db = db
    model = iam_models.User

    @api_view_v1.doc(
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
        return super().get(query)

    @api_view_v1.doc(
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
        return super().patch(query, body)

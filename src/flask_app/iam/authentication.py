from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus
from typing import Optional

from base import schemas as base_schemas
from base.authentication import BaseAuthentication
from flask import (
    g,
    jsonify,
    request
)
from iam import models as iam_models


def protected_view(view_method):
    @wraps(view_method)
    def wrapper(*args, **kwargs):
        view_cls = args[0]
        auth_class = getattr(view_cls, 'authentication_class', None)
        if not auth_class:
            return jsonify({'message': 'No authentication class found'}), HTTPStatus.INTERNAL_SERVER_ERROR

        auth = auth_class()
        if not auth.authenticated:
            return auth.response

        return view_method(*args, **kwargs)

    return wrapper


def superuser_view(view_method):
    @wraps(view_method)
    def wrapper(*args, **kwargs):
        view_cls = args[0]
        auth_class = getattr(view_cls, 'authentication_class', None)
        if not auth_class:
            return jsonify({'message': 'No authentication class found'}), HTTPStatus.INTERNAL_SERVER_ERROR

        auth = auth_class()
        if auth.user:
            if not auth.user.is_superuser:
                auth.authenticated = False
                response_body = base_schemas.UnauthorizedResponseSchema(message='This endpoint is for superusers only').dict()
                auth.response = jsonify(response_body), HTTPStatus.UNAUTHORIZED

        elif not auth.user or not auth.authenticated:
            return auth.response

        return view_method(*args, **kwargs)

    return wrapper


@dataclass
class IAMTokenAuthentication(BaseAuthentication):
    user: Optional[iam_models.User]          = None
    token: Optional[iam_models.IAMAuthToken] = None

    def __init__(self):
        self.__class__.validate_request()

    @classmethod
    def _extract_request_token(cls) -> Optional[str]:
        auth_header = request.headers.get('Authorization', '')
        if auth_header and auth_header.lower().startswith('token '):
            return auth_header.split(' ')[-1]

        return None

    @classmethod
    def validate_request(cls) -> None:
        token_key = cls._extract_request_token()
        if not token_key:
            response_body = base_schemas.UnauthorizedResponseSchema(message='missing authorization header').dict()

            cls.authenticated = False
            cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED
            return

        cls.user = iam_models.User.query.filter(**{'auth_token.key': token_key}).first()
        if not cls.user:
            response_body = base_schemas.UnauthorizedResponseSchema(message='invalid token').dict()

            cls.authenticated = False
            cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED
            return

        if cls.user:
            cls.token = cls.user.token
            g.user    = cls.user

            if not cls.token.is_valid:
                response_body = base_schemas.UnauthorizedResponseSchema(message='expired token').dict()

                cls.authenticated = False
                cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED

        cls.authenticated = True

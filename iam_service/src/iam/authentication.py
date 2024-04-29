from dataclasses import dataclass
from http import HTTPStatus
from typing import Optional

from fim import schemas as base_schemas
from fim.authentication import BaseAuthentication
from flask import (
    g,
    jsonify,
    request
)
from iam import models


@dataclass
class IAMTokenAuthentication(BaseAuthentication):
    user: Optional[models.User]          = None
    token: Optional[models.IAMAuthToken] = None

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

        cls.user = models.User.query.filter(**{'auth_token.key': token_key}).first()
        if not cls.user:
            response_body = base_schemas.UnauthorizedResponseSchema(message='invalid token').dict()

            cls.authenticated = False
            cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED
            return

        if cls.user:
            if not cls.user.token or not cls.user.token.is_valid:
                response_body = base_schemas.UnauthorizedResponseSchema(message='expired token').dict()

                cls.authenticated = False
                cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED
                return

            cls.token         = cls.user.token
            g.user            = cls.user
            cls.authenticated = True

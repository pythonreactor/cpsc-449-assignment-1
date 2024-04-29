from abc import (
    ABC,
    abstractmethod
)
from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus
from typing import (
    Dict,
    Optional
)

from fim.schemas import UnauthorizedResponseSchema
from flask import jsonify
from flask.wrappers import Response as FlaskResponse


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
                response_body = UnauthorizedResponseSchema(message='This endpoint is for superusers only').dict()
                auth.response = jsonify(response_body), HTTPStatus.UNAUTHORIZED

        elif not auth.user or not auth.authenticated:
            return auth.response

        return view_method(*args, **kwargs)

    return wrapper


@dataclass
class BaseAuthentication(ABC):
    authenticated: bool = True
    response: Optional[FlaskResponse] = None

    user: Optional[Dict] = None

    @classmethod
    @abstractmethod
    def validate_request(cls):
        raise NotImplementedError('Calling from the base class')

from dataclasses import dataclass
from http import HTTPStatus
from typing import (
    Dict,
    Optional
)

import requests
from fim import schemas as base_schemas
from fim.authentication import BaseAuthentication
from flask import (
    g,
    jsonify,
    request
)
from inventory import settings


@dataclass
class TokenAuthentication(BaseAuthentication):
    user: Optional[Dict]  = None
    token: Optional[Dict] = None

    def __init__(self):
        self.__class__.validate_request()

    @classmethod
    def _extract_request_token(cls) -> Optional[str]:
        auth_header = request.headers.get('Authorization', '')
        if auth_header and auth_header.lower().startswith('token '):
            return auth_header.split(' ')[-1]

        return None

    @classmethod
    def __prepare_user_data(cls, user_data: Dict) -> None:
        user_data['id'] = base_schemas.FIMObjectID(user_data['id'])
        cls.user = user_data

    @classmethod
    def validate_request(cls) -> None:
        token_key = cls._extract_request_token()
        if not token_key:
            response_body = base_schemas.UnauthorizedResponseSchema(message='missing authorization header').dict()

            cls.authenticated = False
            cls.response      = jsonify(response_body), HTTPStatus.UNAUTHORIZED
            return

        auth_response = requests.post(f'{settings.IAM_SERVICE_API_BASE_URL}/{settings.IAM_SERVICE_ENDPOINTS["authentication"]}', headers={'Authorization': f'token {token_key}'})
        if auth_response.status_code != HTTPStatus.OK:
            cls.authenticated = False
            cls.response      = auth_response.json(), HTTPStatus.UNAUTHORIZED
            return

        auth_data         = auth_response.json()
        cls.token         = auth_data['token']
        cls.authenticated = True

        cls.__prepare_user_data(user_data=auth_data['user'])
        g.user = cls.user

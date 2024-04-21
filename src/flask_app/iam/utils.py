import datetime
import logging

import iam.models as iam_models
from flask import request

from flask_app import settings

logger = logging.getLogger(__name__)


def login_user(user: iam_models.User) -> iam_models.IAMAuthToken:
    """
    Fetch a user's auth token or create a new one
    """
    logger.info('[%s] Generating new user auth token', user.email)
    del user.token

    token      = iam_models.IAMAuthToken()
    user.token = token

    try:
        user.save()
    except Exception:
        logger.exception('Error creating new auth token for user: %s', user.email)
        raise

    return token


class IAMTokenAuthenticator:

    @staticmethod
    def extract_request_token(request) -> str:
        """
        Extract an auth token from a request
        """
        auth_header = request.headers.get('Authorization', '').lower()
        if auth_header.startswith('token '):
            return auth_header.split(' ')[1]

        return None

    @staticmethod
    def verify_token(key: str) -> bool:
        """
        Verify if a token exists and is valid
        """
        token = iam_models.IAMAuthToken.query.filter_by(key=key).first()
        if not token:
            return False

        current_time = datetime.datetime.utcnow()
        timeout_hours = settings.MAX_TOKEN_AGE_SECONDS / (60 ** 2)
        token_age = current_time - token.updated_at

        if token_age > datetime.timedelta(hours=timeout_hours):
            logger.info('Token has expired')
            token.delete()

            return False

        if not token.updated_at == current_time:
            token.updated_at = current_time
            token.save(update_fields=['updated_at'])

        return True


def extract_request_token():
    auth_header = request.headers.get('Authorization').lower()
    if auth_header and auth_header.startswith('token '):
        return auth_header.split(' ')[1]

    return None


def get_current_user():
    token_str = extract_request_token()
    if token_str is None:
        return None

    token = IAMAuthToken.query.filter_by(key=token_str).first()
    if token:
        return token.user

    return None

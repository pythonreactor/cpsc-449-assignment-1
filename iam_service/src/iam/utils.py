import logging

from iam import models

logger = logging.getLogger(__name__)


def login_user(user: models.User) -> models.IAMAuthToken:
    """
    Fetch a user's auth token or create a new one
    """
    logger.info('[%s] Generating new user auth token', user.email)
    del user.token

    token      = models.IAMAuthToken()
    user.token = token

    try:
        user.save()
    except Exception:
        logger.exception('Error creating new auth token for user: %s', user.email)
        raise

    return token

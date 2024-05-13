import logging

from flask import config
from flask_openapi3 import (
    Contact,
    Info
)
from pymongo import IndexModel

# TODO: Move values to ENV variables


# Flask settings
HOST        = '0.0.0.0'
PORT        = 5000
HOSTNAME    = f'http://localhost:{PORT}'
ENVIRONMENT = 'development'
DEBUG       = ENVIRONMENT == 'development'

API_KEY_SCHEME = {
    'type': 'apiKey',
    'in': 'header',
    'name': 'Authorization',
    'description': 'Token <your-token-here>'
}
API_TOKEN_SECURITY = [{'apiKey': []}]
SECURITY_SCHEMES = {'apiKey': API_KEY_SCHEME}

MAX_TOKEN_AGE_SECONDS = 14_400  # 4 hours


# MongoDB settings
MONGO_USERNAME = 'docker'
MONGO_PASSWORD = 'docker'
MONGO_DB_NAME  = 'flask_inventory_management_dev'
MONGO_COLLECTION_NAME = 'users'

MONGO_INDEXES = {
    MONGO_COLLECTION_NAME: [
        IndexModel([('pk')], name='users_pk_unique', unique=True),
        IndexModel([('username')], name='username_unique', unique=True)
    ]
}


# CORS settings
CORS_RESOURCES = {r'/api/v1/iam/*': {'origins': f'http://localhost:{PORT}'}}


# Swagger settings
SWAGGER_DOC_PREFIX = '/api/docs/iam/'
SWAGGER_URL = '/'
SWAGGER_INFO = Info(
    title='Flask Inventory Management IAM API',
    version='3.0.0',
    description="This Flask API was built for CSUF CPSC 449",
    contact=Contact(email='mj.gilbert@csu.fullerton.edu')
)


# OpenAPI3 settings
OPENAPI_APP_CONFIG = dict(
    info=SWAGGER_INFO,
    doc_prefix=SWAGGER_DOC_PREFIX,
    swagger_url=SWAGGER_URL,
    security_schemes=SECURITY_SCHEMES
)


# Logging settings
if DEBUG:
    LOGGING_LEVEL = logging.DEBUG
else:
    LOGGING_LEVEL = logging.INFO

LOG_STREAM_HANDLER = logging.StreamHandler()
LOG_STREAM_FORMATTER = logging.Formatter('%(module)s::%(levelname)s::%(asctime)s: %(message)s')

LOG_STREAM_HANDLER.setLevel(LOGGING_LEVEL)
LOG_STREAM_HANDLER.setFormatter(LOG_STREAM_FORMATTER)

PROPAGATE_LOGS = False


def getLogger(name: str = None):
    """
    Custom method to retrieve a logger instance with a given name
    and set the necessary configurations.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOGGING_LEVEL)
    logger.propagate = PROPAGATE_LOGS

    if not logger.handlers:
        logger.addHandler(LOG_STREAM_HANDLER)

    return logger


# Configuration settings
class FlaskConfig(config.Config):
    DEBUG                = DEBUG
    SECRET_KEY           = 'insecure-secret-key'
    PREFERRED_URL_SCHEME = 'http'

    PERMANENT_SESSION_LIFETIME = 1_800  # 30 minutes
    SESSION_COOKIE_SECURE      = True
    # SESSION_COOKIE_SAMESITE    = ''

    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/{MONGO_DB_NAME}'

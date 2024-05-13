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
MONGO_COLLECTION_NAME = 'inventory'

MONGO_INDEXES = {
    MONGO_COLLECTION_NAME: [
        IndexModel([('pk')], name='users_pk_unique', unique=True)
    ]
}


# Redis settings
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB   = 0

RQ_DASHBOARD_REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
REDIS_RQ_DASHBOARD_URL_PREFIX = '/rq/inventory'


# Elasticsearch settings
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_BASE_URL = 'http://localhost'
ELASTICSEARCH_URL = f'{ELASTICSEARCH_BASE_URL}:{ELASTICSEARCH_PORT}'

INVENTORY_ITEM_INDEX_SETTINGS = {
    'settings': {
        'number_of_shards': 1,
        'number_of_replicas': 0
    },
    'mappings': {
        'properties': {
            'pk': {'type': 'integer'},
            'user_id': {'type': 'text'},
            'name': {'type': 'text'},
            'category': {'type': 'text'},
            'weight': {'type': 'float'},
            'price': {'type': 'float'}
        }
    }
}
ELASTICSEARCH_INDEX_NAME = 'inventory'

ELASTICSEARCH_INDEXES = {
    ELASTICSEARCH_INDEX_NAME: INVENTORY_ITEM_INDEX_SETTINGS
}


# External API settings
# TODO: This should receive its own hostname after NGINX is setup
# TODO: There should also be an interface for accessing this "external service"
IAM_SERVICE_API_PORT     = 5000
IAM_SERVICE_API_BASE_URL = f'http://iam-service:{IAM_SERVICE_API_PORT}/api/v1/iam'
IAM_SERVICE_ENDPOINTS    = {
    'authentication': 'authenticate'
}

# CORS settings
CORS_RESOURCES = {r'/api/v1/inventory/*': {'origins': f'http://localhost:{PORT}'}}


# Swagger settings
SWAGGER_DOC_PREFIX = '/api/docs/inventory/'
SWAGGER_URL = '/'
SWAGGER_INFO = Info(
    title='Flask Inventory Management Inventory API',
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

    REDIS_HOST             = REDIS_HOST
    REDIS_PORT             = REDIS_PORT
    REDIS_DB               = REDIS_DB

    RQ_DASHBOARD_REDIS_HOST = REDIS_HOST
    RQ_DASHBOARD_REDIS_DB   = REDIS_DB
    RQ_DASHBOARD_REDIS_PORT = REDIS_PORT
    RQ_DASHBOARD_REDIS_URL  = RQ_DASHBOARD_REDIS_URL

    ELASTICSEARCH_URL = ELASTICSEARCH_URL

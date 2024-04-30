from flask import config
from flask_openapi3 import (
    Contact,
    Info
)
from pymongo import IndexModel

# TODO: Move values to ENV variables


# Flask settings
HOSTNAME = 'http://localhost:5002'
ENVIRONMENT = 'development'
DEBUG = ENVIRONMENT == 'development'

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


# Elasticsearch settings
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_BASE_URL = 'http://localhost'
ELASTICSEARCH_URL = f'{ELASTICSEARCH_BASE_URL}:{ELASTICSEARCH_PORT}'


# External API settings
# TODO: This should receive its own hostname after NGINX is setup
# TODO: There should also be an interface for accessing this "external service"
IAM_SERVICE_API_BASE_URL = 'http://iam-service:5000/api/v1/iam'
IAM_SERVICE_ENDPOINTS = {
    'authentication': 'authenticate'
}

# CORS settings
CORS_RESOURCES = {r'/api/v1/*': {'origins': 'http://localhost:5000'}}


# Swagger settings
SWAGGER_DOC_PREFIX = '/api/docs'
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


# Configuration settings
class FlaskConfig(config.Config):
    DEBUG                = DEBUG
    SECRET_KEY           = 'insecure-secret-key'
    PREFERRED_URL_SCHEME = 'http'

    PERMANENT_SESSION_LIFETIME = 1_800  # 30 minutes
    SESSION_COOKIE_SECURE      = True
    # SESSION_COOKIE_SAMESITE    = ''

    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/{MONGO_DB_NAME}'

    REDIS_HOST = REDIS_HOST
    REDIS_PORT = REDIS_PORT
    REDIS_DB   = REDIS_DB

    ELASTICSEARCH_URL = ELASTICSEARCH_URL

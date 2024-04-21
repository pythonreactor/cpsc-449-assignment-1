from flask import config
from flask_openapi3 import (
    Contact,
    Info
)
from pymongo import IndexModel

# TODO: Move values to ENV variables


# Flask settings
HOSTNAME = 'http://localhost:5001'
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

MONGO_INDEXES = {
    'users': [
        IndexModel([('pk')], name='users_pk_unique', unique=True),
        IndexModel([('username')], name='username_unique', unique=True)
    ],
    'inventory': [
        IndexModel([('pk')], name='users_pk_unique', unique=True)
    ]
}


# CORS settings
CORS_RESOURCES = {r'/api/v1/*': {'origins': 'http://localhost:5001'}}


# Swagger settings
SWAGGER_DOC_PREFIX = '/api/docs'
SWAGGER_URL = '/'
SWAGGER_INFO = Info(
    title='CPSC 449 Assignment 1 API',
    version='1.0.0',
    description="This Flask API was built for CPSC 449 Assignment 1",
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
    DEBUG = True
    SECRET_KEY = 'insecure-secret-key'
    PREFERRED_URL_SCHEME = 'http'

    PERMANENT_SESSION_LIFETIME = 1_800  # 30 minutes
    SESSION_COOKIE_SECURE = True
    # SESSION_COOKIE_SAMESITE = ''

    MONGO_URI = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@localhost:27017/{MONGO_DB_NAME}'

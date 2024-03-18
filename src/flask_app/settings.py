from flask import config
from flask_openapi3 import (
    Contact,
    Info
)

# TODO: Move values to ENV variables


# Flask settings
HOSTNAME = 'http://localhost:5001'
DEBUG = True

API_KEY_SCHEME = {
    'type': 'apiKey',
    'in': 'header',
    'name': 'Authorization',
    'description': 'Token <your-token-here>'
}
API_TOKEN_SECURITY = [{'apiKey': []}]
SECURITY_SCHEMES = {'apiKey': API_KEY_SCHEME}

MAX_TOKEN_AGE_SECONDS = 14_400  # 4 hours


class FlaskConfig(config.Config):
    DEBUG = True
    SECRET_KEY = 'insecure-secret-key'
    PREFERRED_URL_SCHEME = 'http'

    PERMANENT_SESSION_LIFETIME = 1_800  # 30 minutes
    SESSION_COOKIE_SECURE = True
    # SESSION_COOKIE_SAMESITE = ''

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://docker:docker@cpsc-449-1-mysql/cpsc_449_1_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


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

from flask_cors import CORS
from flask_openapi3 import OpenAPI
from iam import settings

cors = CORS()


def create_app():
    app = OpenAPI(__name__, **settings.OPENAPI_APP_CONFIG)
    app.config.from_object(settings.FlaskConfig)
    cors.init_app(app, resources=settings.CORS_RESOURCES)

    with app.app_context():
        from iam import utils
        from iam.api import service_api_v1

        app.register_api_view(service_api_v1)

        utils.setup_database_indexes()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=settings.HOST)

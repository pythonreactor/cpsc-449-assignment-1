from flask_cors import CORS
from flask_openapi3 import OpenAPI
from inventory import settings

cors = CORS()


def create_app():
    app = OpenAPI(__name__, **settings.OPENAPI_APP_CONFIG)

    app.config.from_object(settings.FlaskConfig)
    cors.init_app(app, resources=settings.CORS_RESOURCES)

    with app.app_context():
        from api import api_view_v1

        app.register_api_view(api_view_v1)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')

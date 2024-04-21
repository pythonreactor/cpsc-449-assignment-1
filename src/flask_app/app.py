from flask_cors import CORS
from flask_openapi3 import OpenAPI

from flask_app import settings

cors = CORS()


def create_app():
    app = OpenAPI(__name__, **settings.OPENAPI_APP_CONFIG)
    app.config.from_object(settings.FlaskConfig)
    cors.init_app(app, resources=settings.CORS_RESOURCES)

    with app.app_context():
        from flask_app.iam.api import api_view_v1 as iam_api_view_v1
        from flask_app.inventory.api import \
            api_view_v1 as inventory_api_view_v1

        app.register_api_view(iam_api_view_v1)
        app.register_api_view(inventory_api_view_v1)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=settings.DEBUG, host='0.0.0.0')

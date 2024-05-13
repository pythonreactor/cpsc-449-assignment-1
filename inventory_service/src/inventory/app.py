from flask_cors import CORS
from flask_openapi3 import OpenAPI
from inventory import settings

cors = CORS()


def create_app():
    app = OpenAPI(__name__, **settings.OPENAPI_APP_CONFIG)

    app.config.from_object(settings.FlaskConfig)
    cors.init_app(app, resources=settings.CORS_RESOURCES)

    with app.app_context():
        from inventory import utils

        utils.setup_database_indexes()
        utils.prepare_es_indexes()

    return app


def register_apis(app: OpenAPI):
    with app.app_context():
        from api import service_api_v1

        app.register_api_view(service_api_v1)

        if settings.DEBUG:
            import rq_dashboard

            rq_dashboard.web.setup_rq_connection(app)
            app.register_blueprint(
                rq_dashboard.blueprint,
                url_prefix=settings.REDIS_RQ_DASHBOARD_URL_PREFIX
            )

    return app


if __name__ == '__main__':
    app = create_app()
    app = register_apis(app)

    app.run(host=settings.HOST)

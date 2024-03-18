from flask_cors import CORS
from flask_migrate import Migrate
from flask_openapi3 import OpenAPI
from flask_sqlalchemy import SQLAlchemy

from flask_app import settings

cors = CORS()
db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = OpenAPI(__name__, **settings.OPENAPI_APP_CONFIG)
    app.config.from_object(settings.FlaskConfig)

    cors.init_app(app, resources=settings.CORS_RESOURCES)
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from flask_app.iam.api import api_view_v1 as iam_api_view_v1

        app.register_api_view(iam_api_view_v1)

    return app


if __name__ == '__main__':
    app = create_app()

    app.run(debug=True, host='0.0.0.0')

from flask import (
    current_app,
    g
)
from flask_pymongo import PyMongo
from iam import settings
from werkzeug.local import LocalProxy

logger = settings.getLogger(__name__)


def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:
        db = g._database = PyMongo(current_app).db

    return db


db = LocalProxy(get_db)

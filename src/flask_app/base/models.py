import datetime
from abc import abstractmethod

from flask_app.app import db


class BaseFlaskModel:
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    @property
    @abstractmethod
    def obj_schema(self) -> dict:
        raise NotImplementedError('Calling from the base class')

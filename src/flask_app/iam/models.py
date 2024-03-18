import binascii
import datetime
import os

import bcrypt

from flask_app import settings
from flask_app.base.models import BaseFlaskModel
from flask_app.iam import db


class IAMAuthToken(db.Model, BaseFlaskModel):
    key = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(64)).decode()

    @property
    def is_valid(self):
        current_time = datetime.datetime.utcnow()
        timeout_hours = settings.MAX_TOKEN_AGE_SECONDS / (60 ** 2)
        token_age = current_time - self.updated_at

        if token_age > datetime.timedelta(hours=timeout_hours):
            db.session.delete(self)

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                pass

            return False

        if not self.updated_at == current_time:
            self.updated_at = current_time

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return True

    @property
    def obj_schema(self):
        return dict(
            key=self.key,
            user_id=self.user_id,
            user_email=self.user.email
        )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.user.email}>'


class User(db.Model, BaseFlaskModel):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    token = db.relationship('IAMAuthToken', backref='user', lazy=True)

    @property
    def password(self):
        raise AttributeError('password not readable')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @property
    def full_name(self):
        return f'{self.first_name.title()} {self.last_name.title()}'

    @property
    def obj_schema(self):
        return dict(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            full_name=self.full_name
        )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.email}>'

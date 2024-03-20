from flask_app.base.models import BaseFlaskModel
from flask_app.inventory import db


class Inventory(db.Model, BaseFlaskModel):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    category = db.Column(db.String(128), nullable=False)

    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    @property
    def obj_schema(self):
        return dict(
            id=self.id,
            name=self.name,
            category=self.category,
            weight=self.weight,
            price=self.price
        )

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

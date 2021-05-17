from api.utils.database import db
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
from api.models.movies import MovieSchema


class Director(db.Model):
    __tablename__ = 'directors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    created = db.Column(db.DateTime, server_default=db.func.now())
    movies = db.relationship('Movie', backref='Director', cascade="all, delete-orphan")

    def __init__(self, first_name, last_name, movies=[]):
        self.first_name = first_name
        self.last_name = last_name
        self.movies = movies

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self


class DirectorSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Director
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    created = fields.String(dump_only=True)
    movies = fields.Nested(MovieSchema, many=True, only=['title','year','id'])
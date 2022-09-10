import datetime

from peewee import CharField, DateTimeField, Model, SQL

from app.providers.database import db


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now())
    updated_at = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


class BaseModelWithSoftDelete(BaseModel):
    deleted_at = DateTimeField(null=True)

    @classmethod
    def undelete(cls):
        return cls.select().where(SQL("deleted_at is NULL"))

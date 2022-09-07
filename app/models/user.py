from peewee import CharField

from app.providers.database import BaseModel


class User(BaseModel):
    class Meta:
        table_name = 'users'

    username = CharField()
    email = CharField()

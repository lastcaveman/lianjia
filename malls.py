from peewee import *

database = MySQLDatabase('malls', **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'user': 'root', 'password': 'pass@dbmima'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Malls(BaseModel):
    address = CharField(null=True)
    area = CharField(null=True)
    city = CharField(null=True)
    desc = CharField(null=True)
    develop = CharField(null=True)
    link = CharField(null=True)
    logo = CharField(null=True)
    name = CharField(null=True)
    ranking = CharField(null=True)
    ranking_str = CharField(null=True)
    start_at = CharField(null=True)

    class Meta:
        table_name = 'malls'


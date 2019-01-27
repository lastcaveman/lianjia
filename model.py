from peewee import *


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Chengjiaos(BaseModel):
    change_price = IntegerField(null=True)
    check = IntegerField(null=True)
    follows = IntegerField(null=True)
    house_code = CharField(null=True)
    period = IntegerField(null=True)
    price = CharField(null=True)
    price_change = DecimalField(null=True)
    signed_at = CharField(null=True)
    source_price = CharField(null=True)
    unit_price = CharField(null=True)
    view = IntegerField(null=True)

    class Meta:
        table_name = 'chengjiaos'

class Communities(BaseModel):
    avg_unit_price = DecimalField(null=True)
    bizcircle_name = CharField(null=True)
    city_name = CharField(null=True)
    district_name = CharField(null=True)
    ershoufang_source_count = IntegerField(null=True)
    name = CharField(null=True)
    source = CharField(null=True)

    class Meta:
        table_name = 'communities'

class Houses(BaseModel):
    bedroom = IntegerField(null=True)
    bizcircle = IntegerField(column_name='bizcircle_id', null=True)
    chengjiao_detail = CharField(null=True)
    city = IntegerField(column_name='city_id', null=True)
    community = CharField(column_name='community_id', null=True)
    desc = CharField(null=True)
    district = IntegerField(column_name='district_id', null=True)
    hall = IntegerField(null=True)
    house_code = CharField(null=True)
    price = CharField(null=True)
    signed_at = CharField(null=True)
    title = CharField(null=True)
    unitprice = CharField(null=True)

    class Meta:
        table_name = 'houses'

class Locations(BaseModel):
    adcode = CharField()
    community = IntegerField(null=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    level = CharField()
    name = CharField()
    parent = CharField(column_name='parent_id')
    quanpin = CharField(constraints=[SQL("DEFAULT ''")])
    updated_at = DateTimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])

    class Meta:
        table_name = 'locations'

class Logs(BaseModel):
    query = CharField(null=True)
    result = CharField(null=True)

    class Meta:
        table_name = 'logs'


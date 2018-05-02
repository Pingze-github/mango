
from tests.mango import *

from tests.mongo import DB

class Article(Model):
    class Meta():
        collection = 'article'
        index = [
            ('item_id', 1)
        ]
        database = DB

    item_id = NumberField(unique=True)
    views = NumberField()
    title = StringField()
    content = StringField()
    title2 = StringField(default='default title2')


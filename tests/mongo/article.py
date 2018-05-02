
from tests.mango import *

from tests.mongo import DB

class Article(Model):
    class Meta():
        collection = 'article'
        index = [
            ('item_id', 1)
        ]
        database = DB

    item_id = IntField(unique=True)
    title = StringField()
    content = StringField()


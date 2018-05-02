
from tests.mango import *

from tests.mongo import DB

class Dictionary(Model):
    class Meta():
        collection = 'dictionary'
        database = DB

    id = IntField()
    words = ListField()
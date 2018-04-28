from tests.mango import *

class Article(Model):
    class Meta():
        collection = 'article'
        index = [
            'item_id'
        ]
        # TODO 在这里声明db，才能正常做初始化工作(声明子类时操作)
        database = db

    item_id = IntField()
    title = StringField()
    content = StringField()


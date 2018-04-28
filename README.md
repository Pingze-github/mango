# mango
Python3 Mongodb ORM (开发中)

轻量级 Mongodb ORM。封装自 pymongo。

### TODO 
+ 动态添加所有方法
+ 有效封装find，支持直接迭代返回model对象
+ 支持连接多个库(db的保存方式)

### 示例

``` python

from .mango import *

conn, db = connect(
    ip='127.0.0.1',
    port=27017,
    database='recommender'
)

class Article(Model):
    class Meta():
        database = db
        collection = 'article'
        index = [
            'item_id'
        ]

    item_id = IntField()
    title = StringField()
    content = StringField()
    
# 查出一个    
doc = Article.find_one()

# 迭代查询
for doc in Article.find():
    print(Article(doc))
```


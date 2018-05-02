# mango
Python3 Mongodb ORM (开发中)

轻量级 Mongodb ORM。封装自 pymongo。

### TODO 
+ ~~动态添加所有方法~~
+ ~~有效封装find，支持直接迭代返回model对象~~
+ ~~支持连接多个库(db的保存方式)~~
+ ~~支持索引~~
+ 支持高级方法
+ 支持对更新等方法的验证

### 示例

``` python

from .mango import *

# 创建连接
conn, DB = connect(
    ip='127.0.0.1',
    port=27017,
    database='recommender'
)

# 声明Model
class Article(Model):
    class Meta():
        database = DB
        collection = 'article'
        index = [
            ('title', 1)
        ]

    # 不包含_id，由mongo自动生成
    id = IntField(unique=True)
    title = StringField()
    content = StringField()
    
# 查出一个    
doc = Article.find_one()

# 迭代查询
for doc in Article.find():
    # 将查出的字典转为Model对象
    print(Article(doc))
    
# 添加
_id = Article.create(
    id = 1
    title = 'test title'
    content = 'test_content'
)

# 添加(pymong原生)
_id = Article.insert({
    'id': 1
    'title': 'test title'
    'content': 'test_content'
})

# 更新(pymong原生)
Article.update(
    {
        'id': 1
    },{
        'id': 1,
        'title': 'test1',
        'content': 'test too',
    },
    # True表示upsert
    True
)

# 移除(pymongo原生)
Article.remove({'id': 1})

```



from tests.mongo.article import Article
from tests.mongo.dictionary import Dictionary

Dictionary.find()

doc = Article.find_one()
print(doc.item_id)
print(doc.title)

cursor = Article.find()
# for i in Article.find().sort(Article.item_id, -1): 这里原生不能支持转str
for i in Article.find().sort(Article.item_id.name, -1):
    print(Article(**i).item_id)
    print(Article(i).title)

print(Article.create(
    item_id=2,
    title='test',
    content='test too',
    type=1
))

# print(Article.update({
#     'item_id': 1
# },{
#     'item_id': 1,
#     'title': 'test1',
#     'content': 'test too',
#     'type': 1
# },True))

# print(Article.remove({
#     'item_id': 1
# }))

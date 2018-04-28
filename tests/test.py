
from tests.mongo.article import Article

doc = Article.find_one()
print(doc.item_id)
print(doc.title)

cursor = Article.find()
for i in Article.find():
    print(Article(**i).item_id)
    print(Article(i).title)
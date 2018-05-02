from tests.mango import connect

# 这里已经改变了mango中的db和conn
CONN, DB = connect(
    host='127.0.0.1',
    port=27017,
    database='recommender'
)

# mongo的ORM库
# 宗旨：
# API尽量贴合mongo原生pymongo
# 转换pymongo的字典为对象
# 具有简单的校验，
# 可管理index

from pymongo import MongoClient

global connection
global db
connection = None
db = None

# ****** connect *******

def connect(
    database,
    ip='127.0.0.1',
    port=27017,
    username=None,
    password=None,
):
    global connection, db
    connection = MongoClient(
        ip,
        port,
        username=username,
        password=password,
        authSource=database
    )
    db = connection[database]
    return connection, db

# ****** Fields ******

class Field(object):
    _type = object
    def field_assert(self, value, name):
        if not isinstance(value, self._type):
            raise TypeError('document.{} given not match the field "{}". It\'s class is "{}"'
                            .format(name, self.__class__.__name__, value.__class__.__name__))

class IntField(Field):
    _type = int

class StringField(Field):
    _type = str

class ListField(Field):
    _type = list

class DictField(Field):
    _type = dict


# ****** Model ******

class Model(object):
    class Meta():
        strict = False
        collection = None
        index = None
        database = db

    # Python3.6及以上
    def __init_subclass__(subcls, **kargs):
        subcls.Meta.collection = subcls.Meta.collection if hasattr(subcls.Meta, 'collection') else subcls.__name__.lower()
        if subcls.Meta.index:
            print(subcls.Meta.database)
            collection = subcls.Meta.database[subcls.Meta.collection]
            print(collection)

    def __init__(self, *args, **kargs):
        if args and not kargs and type(args[0]) == dict:
            dict_data = args[0]
            kargs = (lambda **kargs: kargs)(**dict_data)
        for attr_name in dir(self):
            field = self.__getitem__(attr_name)
            if isinstance(field, Field):
                if attr_name in kargs:
                    kargs_v = kargs[attr_name]
                    field.field_assert(kargs_v, attr_name)
                    self.__setitem__(attr_name, kargs_v)
                else:
                    if self.__class__.Meta.strict:
                        raise AttributeError('Model.{} not exists in real document'.format(attr_name))
                    else:
                        self.__setitem__(attr_name, None)


    def __getitem__(self, k):
        return getattr(self, k)

    def __setitem__(self, k, v):
        setattr(self, k, v)

    @classmethod
    def find_one(cls, *args, **kargs):
        data_dict = db[cls.Meta.collection].find_one(*args, **kargs)
        return cls.dict2obj(data_dict)

    @classmethod
    def dict2obj(cls, data_dict):
        return cls(**data_dict)

    @classmethod
    def find(cls, *args, **kargs):
        cursor = db[cls.Meta.collection].find(*args, **kargs)
        return cursor

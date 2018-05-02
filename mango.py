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
    name = None

    def __init__(self, field_name=None):
        self.name = field_name

    def __str__(self):
        return self.name

    def field_assert(self, value, name='?'):
        if not isinstance(value, self._type):
            raise TypeError('document.{} given not match the field "{}". It\'s class is "{}"'
                            .format(name, self.__class__.__name__, value.__class__.__name__))

    def setname(self, name):
        self.name = name


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
    find = None
    find_one = None
    insert = None
    create = None
    update = None
    remove = None

    class Meta():
        strict = False
        collection = None
        index = None
        database = db

    # Python3.6及以上
    def __init_subclass__(subcls, **kargs):
        subcls.Meta.collection = subcls.Meta.collection if hasattr(subcls.Meta, 'collection') else subcls.__name__.lower()
        if hasattr(subcls.Meta, 'index'):
            collection = subcls.Meta.database[subcls.Meta.collection]
            print(collection)

    def __init__(self, *args, **kargs):
        if args and not kargs and type(args[0]) == dict:
            dict_data = args[0]
            kargs = (lambda **kargs: kargs)(**dict_data)
        for attr_name in dir(self):
            field = self.__getitem__(attr_name)
            if isinstance(field, Field):
                if not field.name:
                    field.setname(attr_name)
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
    def dict2obj(cls, data_dict):
        return cls(**data_dict)

    @classmethod
    def filte_field(cls, field_dict):
        for key in field_dict:
            val = field_dict[key]
            if not hasattr(cls, key) or not isinstance(getattr(cls, key), Field):
                continue
            getattr(cls, key).field_assert(val, key)

@classmethod
def find(cls, *args, **kargs):
    cursor = db[cls.Meta.collection].find(*args, **kargs)
    # 可以实现直接返回Model对象，但这样返回字典手动转换，更灵活
    return cursor

@classmethod
def find_one(cls, *args, **kargs):
    data_dict = db[cls.Meta.collection].find_one(*args, **kargs)
    return cls.dict2obj(data_dict)

@classmethod
def insert(cls, *args, **kargs):
    cls.filte_field(args[0])
    _id = db[cls.Meta.collection].insert(*args, **kargs)
    return _id

@classmethod
def create(cls, **kargs):
    cls.filte_field(kargs)
    _id = db[cls.Meta.collection].insert(kargs)
    return _id

@classmethod
def update(cls, *args, **kargs):
    # cls.filte_field(args[0])
    # TODO pymongo的update使用多重字典，无法直接做检查
    returned = db[cls.Meta.collection].update(*args, **kargs)
    return returned

@classmethod
def remove(cls, *args, **kargs):
    # cls.filte_field(args[0])
    # TODO pymongo的remove使用多重字典，无法直接做检查
    returned = db[cls.Meta.collection].remove(*args, **kargs)
    return returned

setattr(Model, 'find', find)
setattr(Model, 'find_one', find_one)
setattr(Model, 'insert', insert)
setattr(Model, 'create', create)
setattr(Model, 'update', update)
setattr(Model, 'remove', remove)

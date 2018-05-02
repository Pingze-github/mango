# a Mongodb ORM
# 贴近原生的API | 简单的声明方式 | 完整的基本功能

from pymongo import MongoClient, errors

__all__ = ['connection', 'db', 'BoolField', 'IntField', 'FloatField', 'NumberField', 'StringField', 'ListField', 'DictField', 'Model']

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
    default = None

    def __init__(self, field_name=None, index=False, unique=False, default=None):
        self.name = field_name
        self.index = index
        self.unique = unique
        self.default = default if default else self.default

    def __str__(self):
        return self.name

    def field_assert(self, value, name='?'):
        if type(self._type) != list:
            self._type = [self._type]
        if not type(value) in self._type and value != None:
            raise TypeError('document.{} given not match the field "{}". It\'s class is "{}"'
                            .format(name, self.__class__.__name__, value.__class__.__name__))

    def setname(self, name):
        self.name = name

class BoolField(Field):
    _type = bool
    default = False

class NumberField(Field):
    _type = [int, float]
    default = 0

class IntField(Field):
    _type = int
    default = 0

class FloatField(Field):
    _type = float
    default = 0.0

class StringField(Field):
    _type = str
    default = ''

class ListField(Field):
    _type = list
    default = []

class DictField(Field):
    _type = dict
    default = {}

# ****** Model Funcs ******

def cls_method_creater(func_name):
    '直接生成pymongo原生方法的包装类方法'
    @classmethod
    def func(cls, *args, **kargs):
        # args[0]为插入字段时，做替换，清除未声明的field
        if func_name in ['insert', 'create']:
            args = (cls.filte_field(args[0]),) + args[1:]
        else:
            cls.filte_field(args[0])
        func_real = getattr(db[cls.Meta.collection], func_name)
        returned = func_real(*args, **kargs)
        return returned
    return func

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
    args = (cls.filte_field(args[0]),) + args[1:]
    _id = db[cls.Meta.collection].insert(*args, **kargs)
    return _id

@classmethod
def create(cls, **kargs):
    kargs = cls.filte_field(kargs)
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


# ****** Model ******

class Model(object):
    find = find
    find_one = find_one
    insert = cls_method_creater('insert')
    create = create
    update = cls_method_creater('update')
    remove = cls_method_creater('remove')
    insert_many = cls_method_creater('insert_many')
    insert_one = cls_method_creater('insert_one')
    index_information = cls_method_creater('index_information')
    update_many = cls_method_creater('update_many')
    ensure_index = cls_method_creater('ensure_index')
    drop_indexes = cls_method_creater('drop_indexes')
    drop_index = cls_method_creater('drop_index')
    delete_one = cls_method_creater('delete_one')
    delete_many = cls_method_creater('delete_many')
    create_indexes = cls_method_creater('create_indexes')
    create_index = cls_method_creater('create_index')
    count = cls_method_creater('count')
    aggregate = cls_method_creater('aggregate')

    class Meta():
        strict = False
        collection = None
        index = None
        database = db

    # Python3.6及以上
    def __init_subclass__(subcls, **kargs):
        subcls.Meta.collection = subcls.Meta.collection if hasattr(subcls.Meta, 'collection') else subcls.__name__.lower()
        collection = subcls.Meta.database[subcls.Meta.collection]
        if hasattr(subcls.Meta, 'index'):
            for index in subcls.Meta.index:
                try:
                    collection.create_index([index])
                except errors.OperationFailure:
                    pass
        for attr_name in dir(subcls):
            field = getattr(subcls, attr_name)
            if isinstance(field, Field):
                try:
                    if field.unique:
                        collection.create_index([(attr_name, -1 if field.index == -1 else 1)], unique=True)
                    elif field.index:
                        collection.create_index([(attr_name, -1 if field.index == -1 else 1)])
                except errors.OperationFailure:
                    pass

    def __init__(self, *args, **kargs):
        if args and not kargs and type(args[0]) == dict:
            dict_data = args[0]
            kargs = (lambda **kargs: kargs)(**dict_data)
        for attr_name in dir(self):
            field = self.__getitem__(attr_name)
            if isinstance(field, Field):
                if not field.name:
                    field.setname(attr_name)
                if field.name in kargs:
                    kargs_v = kargs[field.name]
                    field.field_assert(kargs_v, attr_name)
                    self.__setitem__(attr_name, kargs_v)
                else:
                    if hasattr(self.__class__.Meta, 'strict') and self.__class__.Meta.strict:
                        raise AttributeError('Model.{} not exists in real document'.format(attr_name))
                    else:
                        self.__setitem__(attr_name, field.default if field.default != None else None)


    def __getitem__(self, k):
        return getattr(self, k)

    def __setitem__(self, k, v):
        setattr(self, k, v)

    @classmethod
    def dict2obj(cls, data_dict):
        return cls(**data_dict)

    @classmethod
    def filte_field(cls, field_dict):
        new_dict = {}
        for key in field_dict:
            val = field_dict[key]
            if not hasattr(cls, key) or not isinstance(getattr(cls, key), Field):
                continue
            getattr(cls, key).field_assert(val, key)
            new_dict[key] = val

        for attr_name in dir(cls):
            field = getattr(cls, attr_name)
            if isinstance(field, Field):
                if field.name in field_dict:
                    val = field_dict[field.name]
                    field.field_assert(val, field.name)
                    new_dict[field.name] = val
                else:
                    if field.default != None:
                        new_dict[field.name] = field.default

        return new_dict

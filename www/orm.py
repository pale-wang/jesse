import aiomysql
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def create_pool(loop, **kw):
    logging.info('create database connection pool')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


async def select(sql, args, size=None):
    global __pool
    async with __pool.acquire() as conn:
        # 采用DictCursor是因为：比如findAll最后返回的cls(**r)中的r需要使用dict
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # execute的第二个参数为tuple,代表values(xxx,xxx)中的参数
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
    return rs


async def execute(sql, args):
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class ModelMetaclass(type):

    """
    cls:
    name: 什么含义
    bases:
    attrs:
    """
    def __new__(cls, name, bases, attrs):
        #如果是Model类，不需要额外的处理，直接走默认的流程即可。
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        # 从Model中获取到需要绑定的__table__名称
        table_name = attrs.get('__table__', None) or name

        mappings = dict()
        fields = []
        primaryKey = None
        #遍历attrs.items()获得的(k,v)对是什么含义
        # k,v =>  email = StringField(ddl='varchar(50)')
        #
        for k,v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)

        if not primaryKey:
            raise RuntimeError('Primary key not found')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))

        attrs['__mappings__'] = mappings

        #存储数据库表名
        attrs['__table__'] = table_name
        #存储primary_key的field名称
        attrs['__primary_key__'] = primaryKey
        #存储fields名称，是否包含primary_key?
        attrs['__fields__'] = fields

        #select id, email, passwd, admin, name, image, create_at from users
        attrs['__select__'] = 'select `{}`, {} from `{}`'.format(primaryKey, ', '.join(escaped_fields), table_name)

        #最后要形成的insert语句格式为：insert into users(,`id`) value()
        attrs['__insert__'] = 'insert into `{}` ({}, `{}`) values ({})'\
            .format(table_name,
                    ', '.join(escaped_fields),
                    primaryKey,
                    create_args_string(len(escaped_fields) + 1))

        #update `users` set name=? where `id`=?
        #lambda表达式将f为从mappings中获取f
        #f 参数来自fields
        #设置为 mappings.get(f).name or f
        attrs['__update__'] = 'update `{}` set %s where `%s`=?'\
            .format(table_name,
                    ', '.join(map(lambda f: '`{}`=?'.format(mappings.get(f).name or f), fields)),
                    primaryKey)

        #delete from users where id=?
        attrs['__delete__'] = 'delete from `{}` where `{}`=?'.format(table_name, primaryKey)

        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    #下面整个函数没看懂
    #获取field的
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            #mappings__中存储的是 id=>FieldString()de
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, value))
                setattr(self, key, value)
        return value

    @classmethod
    async def find(cls, pk):
        logging.info('find is called pk:' + str(pk))
        #logging.info(cls.__select__)
        logging.info('{} where `{}`=?'.format(cls.__select__, cls.__primary_key__))
        rs = await select('{} where `{}`=?'.format(cls.__select__, cls.__primary_key__), [pk], 1)
        #print(rs[0])
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        'find objects by where clause.'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)

        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)

        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        logging.info(' '.join(sql))
        rs = await select(' '.join(sql), args)
        # for r in rs:
        #    print(r)
        #    print(type(r))
        # print(rs)
        # 这行代码怎么理解 , 因为当前这个类，继承自dict,所以可以用**r进行初始化
        # print(cls)
        return [cls(**r) for r in rs]
        #print(cls)
        #print(res)
        #return res

    async def save(self):
        #先获取各个字段的值
        args = list(map(self.getValueOrDefault, self.__fields__))
        #再添加上主键的值
        args.append(self.getValueOrDefault(self.__primary_key__))
        #执行插入
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warnning('failed to insert record: affected rows:%s' % rows)



"""
name => mysql中的字段名
cloumn_type => mysql中的字段类型
primary_key => 是否为主键
default     => 默认值
"""
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<{}, {}:{}>'.format(self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=None):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None):
        super().__init__(name, 'real', primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, primary_key=False, default=None):
        super().__init__(name, 'bool', primary_key, default)

class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)

async def test(loop):
    await create_pool(loop=loop, user='root', password='root', db='jesse')
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            affected = await cur.execute('insert test(name) values("wangsheng04")')
            print(affected)

async def test_select(loop):
    await create_pool(loop=loop, user='root', password='root', db='jesse')
    rs = await select('select * from test where name=?', ('xiangdong',))
    print(rs)

async def test_save(loop):
    await create_pool(loop=loop, user='root', password='root', db='jesse')
    user = User()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_select(loop))
    finally:
        print('closing event loop')
        loop.stop()

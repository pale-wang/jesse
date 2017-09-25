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
        async with conn.cursor() as cur:
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


async def test(loop):
    await create_pool(loop=loop, user='root', password='root', db='jesse')
    async with __pool.acquire() as conn:
        async with conn.cursor() as cur:
            affected = await cur.execute('insert test(name) values("wangsheng04")')
            print(affected)

async def test_select(loop):
    await create_pool(loop=loop, user='root', password='root', db='awesome')
    rs = await select('select * from users where name like ?', ('Test%',))
    print(rs)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_select(loop))
    finally:
        print('closing event loop')
        loop.stop()

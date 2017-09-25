import orm
from models import User, Blog
import asyncio

"""
async def test(loop):
    await orm.create_pool(loop=loop, user='root', password='root', db='awesome')
    u = User(name='Test1', email='test1@example.com', passwd='1234567890', image='about:blank')
    await u.save()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(test(loop))
    finally:
        print('closing event loop')
        loop.close()
"""

"""
async def test_insert(loop):
    await orm.create_pool(loop=loop, user='root', password='root', db='awesome')
    rs = await orm.execute('insert into users(id, email, passwd, admin, name, image, created_at) values (?, ?, ?, ?, ?, ?, ?)', ('11112', 'orm_new2@example.com', '1234567890', 0, 'orm_new', 'blank:orm_new', 0.0))
    print(rs)
"""
async def test_findAll(loop):
    await orm.create_pool(loop, user='root', password='root', db='awesome')
    await User.findAll()

async def test_insert(loop):
    await orm.create_pool(loop=loop, user='root', password='root', db='awesome')
    u = User(name='王盛', email='wstnap@gmail.com', passwd='wshyWS1990', image='about:blank')
    await u.save()

async def test_blog_insert(loop):
    await orm.create_pool(loop=loop, user='root', password='root', db='awesome')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_insert(loop))
    finally:
        print('closing event loop')
        loop.stop()
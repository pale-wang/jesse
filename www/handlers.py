import functools
import inspect
from urllib import parse
import logging
import os
import asyncio
from orm import create_pool
from coroweb import get
from models import User, Comment, Blog, next_id


"""
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
"""

@get('/register')
async def register(request):
    return {
        '__template__':'register.html',
    }

#@post('/api/users')
def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not email.strip():
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in user.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120', % hashlib.md5(email,encode('utf-8')).hexdigest())
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd= '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

@get('/')
async def index(request):
    blogs = await Blog.findAll()
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/blogs')
async def blogs(request):
    blogs = await Blog.findAll()
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/blog/{id}')
async def get_blog(id):
    logging.info("get_blog id:" + str(id))
    blog = await Blog.find(id)
    return {
        '__template__': 'blog.html',
        'blog': blog
    }

@get('/tutorials')
async def tutorial(request):
    return {
        '__template__': 'tutorials.html',
    }

@get('/fun')
async def fun(request):
    return {
        '__template__': 'fun.html',
    }

async def test(loop):
    await create_pool(loop=loop, user='root', password='root', db='awesome')
    request = []
    res = await index(request)
    print(res)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop=loop))




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




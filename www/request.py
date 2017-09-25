import asyncio
import functools

def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__  = path
        return wrapper
    return decorator


class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn


    async def __call__(self, request):

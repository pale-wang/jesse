import functools
import os
import logging
import asyncio
import inspect
from aiohttp import web

logging.basicConfig(level=logging.INFO)

# 第一层是为了携带装饰器的参数
def get(path):
    # 第二层传递的参数是被装饰的函数
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 第二层装饰，为将要返回的函数附加两个参数 __method__ 和 __route__
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
    return found

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

class RequestHandler(object):
    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        logging.info("found _has_request_arg:" + str(self._has_request_arg))
        logging.info("found _has_named_kw_args:" + str(self._has_named_kw_args))
    async def __call__(self, request):
        #kw = None
        # logging.info("----kw-----:"+ str(kw))
        # match_info中存储的是/blog/{id}这样的捕获到的参数
        kw = dict(**request.match_info)
        #print(kw)
        if self._has_request_arg:
            try:
                r = await self._func(request)
                return r
            except Exception as e:
                logging.error("RequestHandler __call__ error")
        elif kw is not None:
            try:
                r = await self._func(**kw)
                print(r)
                return r

            except Exception as e:
                logging.error("RequestHandler __call__ error")

# app.router是个什么结构？
# 将URL请求的path中的static映射到本地的路径
def add_static(app):
    print(__file__)
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    logging.info('static path is ' + path)
    app.router.add_static('/static/', path)
    logging.info('add static {} => {}'.format('/static/', path))


# 这个函数又获取了一遍method, path, 并做了检查
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    logging.info('{} method found:{}'.format(str(fn), method))
    logging.info('{} route  found:{}'.format(str(fn), path))
    if method is None or path is None:
        raise ValueError('@get or @post is not defined in {}'.format(str(fn)))

    #如果不是协程，将函数变为协程
    if not asyncio.iscoroutine(fn):
        fn = asyncio.coroutine(fn)
    # !!核心就是这一句，
    # 把path的处理函数RequestHandler(app,fn), 附加到method(GET,POST) 的 path上。
    # 第三个参数的含义是什么？
    # 第三个参数其实是创建了一个新的RequestHandler的对象
    # AssertionError: Handler <function AbstractRoute.__init__.<locals>.handler_wrapper at 0x103c3c950> should return response instance, got <class 'NoneType'> [middlewares []]
    # 出问题应该就出现在这个地方
    # 传递给RequestHandler的参数为 app, index
    app.router.add_route(method, path, RequestHandler(app, fn))

    """
     if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutine(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.route.add_route(method, path, RequestHandler(app,fn))
    """

def handler(Request):
    return web.Response(text='Hello, {}'.format(Request.match_info.get('name', 'Anonymous')))


def test_add_routes(app):
    resource = app.router.add_resource('/name/{name}')
    resource.add_route('GET', handler)
    app.router.add_get('/name', handler)
    add_routes(app, 'handlers')

def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
        print(mod)
    else:
        logging.error("Can't find {} module".format(module_name))

    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            logging.info('handler fn found: {}'.format(str(fn)))
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                logging.info("handler fn method: {}".format(method))
                logging.info("handler fn path:   {}".format(path))
                add_route(app, fn)

def test_getId(id):
    pass

if __name__ == '__main__':
    #pp = []
    #add_routes(app, 'handlers')
    print(get_required_kw_args(test_getId))
    print(has_named_kw_args(test_getId))
    print(has_var_kw_arg(test_getId))

from jinja2 import Environment, FileSystemLoader
from aiohttp import web
import logging
import asyncio
import os
import json
import orm
from coroweb import add_routes, add_static, test_add_routes

logging.basicConfig(level=logging.INFO)

def index(request):
    return web.Response(body=b'<html><h1>Awesome<h1></html>')

def init_jinja2(app, **kw):
    #对于第一次使用来说，options完全可以没有。
    #作为严格的程序员这种习惯是好的。但是作为教程可以说是装逼的嫌疑太大
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        #获取当前文件的绝对路径，以此获取templates目录
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 templates path:{}'.format(path))
    env = Environment(loader=FileSystemLoader(path), **options)
    app['__templating__'] = env


# 是要作为decorator使用
async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: {} {}'.format(request.method, request.path))
        return (await handler(request))
    return logger


# decorator的作用，打log, 对返回类型进行处理
async def response_factory(app, handler):
    async def response(request):
        logging.info("Response handler...")
        # 调用handler来处理url请求，并返回结果
        r = await handler(request)
        # add_static返回的是什么类型的？
        #print("=================="+ type(r))
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, dict):
            template = r['__template__']
            if template is  None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o:o.__dict__).encode('utf-8'))
                resp.content_type = 'text/html; charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        ## 在这里做了r的类型判断，默认先设置为str,方便处理
        resp = web.Response(body=str(r).encode("utf-8"))
        resp.content_type = "text/plain;charset=utf-8"
        return resp
    return response


def handler(Request):
    return web.Response(text='Hello, {}'.format(Request.match_info.get('name', 'Anonymous')))


async def init(loop):
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='root', db='awesome')
    # 这一行是重点
    # loop 指的是asyncio中的loop
    # middleware是个什么东西
    # middleware挺重要的一个东西，没有他，返回的结果不是一个Response
    app = web.Application(loop=loop, middlewares=[response_factory])
    test_add_routes(app)

    # 暂时先不使用middleware机制，看完aiohttp再来处理
    # #, middlewares=[logger_factory, response_factory])
    init_jinja2(app)
    add_routes(app, 'handlers')
    add_static(app)
    #app.router.add_static('/static', '/Users/wangsheng04/PycharmProjects/PythonLearning/aiohttp')
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    return srv



"""
if __name__ == '__main__':
    app = {}
    init_jinja2(app)
    test_template = app['__templating__'].get_template('test.html')
    u = [{'name': 'wangsheng04', 'email': 'wangsheng04@baidu.com'}, ]
    print(test_template.render(users=u))
"""


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


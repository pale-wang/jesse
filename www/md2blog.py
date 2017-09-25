from pathlib import Path
import asyncio
import orm
from models import Blog
from markdown2 import Markdown

class MdHandler(object):
    def __init__(self, path):
        self._path = path
        self._blogfields = dict()

    async def parse(self):
        markdowner = Markdown()
        with open(self._path) as f:
            for line in f:
                if(line.startswith('___')):
                    meta_key = line.split('=')[0][3:]
                    meta_value = line.split('=')[1]
                    self._blogfields[meta_key] = meta_value
                else:
                    break
            buffer = f.read()
            self._blogfields['content'] = markdowner.convert(buffer)
            #如何遍历dict
            for k,v in self._blogfields.items():
                print(k + ":" + v)
            blog = Blog(user_id='1505380110000aebbb1b79bde4ee5819658105206ddb7000',
                        user_name='王盛',
                        user_image='about:blank',
                        name=self._blogfields['name'],
                        summary=self._blogfields['summary'],
                        content=self._blogfields['content'])
            await blog.save()

async def importBlog():
    await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='root', db='awesome')
    p = Path('./markdown')
    for x in p.iterdir():
        file_path = str(x)
        if file_path.endswith('.md'):
            await MdHandler(file_path).parse()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(importBlog())

#importBlog()



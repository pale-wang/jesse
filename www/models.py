from orm import Model, StringField, IntegerField, FloatField, TextField, BooleanField

import time, uuid

def next_id():
    return '%15d%s000' % (int(time.time()) * 1000, uuid.uuid4().hex)


class DBConfig(Model):
    __table__ = 'dbconfig'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')


class User(Model):
    __table__ = 'users'

    # default为什么是next_id的函数名
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField(default=False)
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time())


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True)
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time())


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id)
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time())







